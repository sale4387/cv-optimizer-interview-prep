from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    PTOContainer,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from cv_data.models import CVProfile
from logger import logger
from services.cv_content_rules import (
    filter_responsibilities,
)


MAX_PDF_PAGES = 2
PROJECTS_TO_RENDER = 3

FONT_SCALE_ATTEMPTS = (
    1.00,
    0.95,
    0.90,
    0.85,
    0.80,
    0.75,
)

REGULAR_FONT_PATHS = (
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
)

BOLD_FONT_PATHS = (
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
)


class PDFRenderError(RuntimeError):
    """Controlled error raised when the CV PDF cannot be generated safely."""


def _find_font(paths: tuple[Path, ...]) -> Path:
    for path in paths:
        if path.exists():
            return path

    raise PDFRenderError(
        "No supported Unicode font was found for PDF generation."
    )


def _register_fonts() -> tuple[str, str]:
    regular_name = "CVUnicode"
    bold_name = "CVUnicode-Bold"

    registered = set(pdfmetrics.getRegisteredFontNames())

    if regular_name not in registered:
        pdfmetrics.registerFont(
            TTFont(
                regular_name,
                str(_find_font(REGULAR_FONT_PATHS)),
            )
        )

    if bold_name not in registered:
        pdfmetrics.registerFont(
            TTFont(
                bold_name,
                str(_find_font(BOLD_FONT_PATHS)),
            )
        )

    return regular_name, bold_name


def _text(value: Any) -> str:
    return escape(str(value))


def _build_styles(
    *,
    regular_font: str,
    bold_font: str,
    scale: float,
) -> dict[str, ParagraphStyle]:
    return {
        "name": ParagraphStyle(
            "CVName",
            fontName=bold_font,
            fontSize=18 * scale,
            leading=20 * scale,
            textColor=colors.HexColor("#173F5F"),
            spaceAfter=2.5 * mm * scale,
        ),
        "contact": ParagraphStyle(
            "CVContact",
            fontName=regular_font,
            fontSize=7.8 * scale,
            leading=9.2 * scale,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=3 * mm * scale,
        ),
        "section": ParagraphStyle(
            "CVSection",
            fontName=bold_font,
            fontSize=9.4 * scale,
            leading=10.8 * scale,
            textColor=colors.HexColor("#173F5F"),
            spaceBefore=2.2 * mm * scale,
            spaceAfter=1.3 * mm * scale,
            borderWidth=0,
            borderPadding=0,
        ),
        "body": ParagraphStyle(
            "CVBody",
            fontName=regular_font,
            fontSize=8.15 * scale,
            leading=9.7 * scale,
            textColor=colors.HexColor("#18202B"),
            alignment=TA_LEFT,
            spaceAfter=1.3 * mm * scale,
        ),
        "skills": ParagraphStyle(
            "CVSkills",
            fontName=regular_font,
            fontSize=7.8 * scale,
            leading=9.2 * scale,
            textColor=colors.HexColor("#18202B"),
            spaceAfter=1.5 * mm * scale,
        ),
        "entry_title": ParagraphStyle(
            "CVEntryTitle",
            fontName=bold_font,
            fontSize=8.45 * scale,
            leading=9.8 * scale,
            textColor=colors.HexColor("#18202B"),
        ),
        "entry_date": ParagraphStyle(
            "CVEntryDate",
            fontName=regular_font,
            fontSize=7.2 * scale,
            leading=8.5 * scale,
            textColor=colors.HexColor("#4B5563"),
            alignment=2,
        ),
        "meta": ParagraphStyle(
            "CVMeta",
            fontName=regular_font,
            fontSize=7.15 * scale,
            leading=8.4 * scale,
            textColor=colors.HexColor("#626B78"),
            spaceAfter=0.9 * mm * scale,
        ),
        "bullet": ParagraphStyle(
            "CVBullet",
            fontName=regular_font,
            fontSize=7.75 * scale,
            leading=9.1 * scale,
            textColor=colors.HexColor("#18202B"),
            leftIndent=0,
            firstLineIndent=0,
            spaceAfter=0.15 * mm * scale,
        ),
        "small_bold": ParagraphStyle(
            "CVSmallBold",
            fontName=bold_font,
            fontSize=7.6 * scale,
            leading=8.9 * scale,
            textColor=colors.HexColor("#18202B"),
            leftIndent=3 * mm * scale,
            spaceBefore=0.8 * mm * scale,
            spaceAfter=0.35 * mm * scale,
        ),
        "small": ParagraphStyle(
            "CVSmall",
            fontName=regular_font,
            fontSize=7.4 * scale,
            leading=8.8 * scale,
            textColor=colors.HexColor("#18202B"),
            spaceAfter=1 * mm * scale,
        ),
    }


def _section_heading(
    title: str,
    styles: dict[str, ParagraphStyle],
) -> list:
    rule = Table(
        [[Paragraph(_text(title.upper()), styles["section"])]],
        colWidths=[None],
    )

    rule.setStyle(
        TableStyle(
            [
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CFD6DF"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
            ]
        )
    )

    return [rule, Spacer(1, 0.8 * mm)]


def _bullet_list(
    items: list[str],
    styles: dict[str, ParagraphStyle],
    *,
    indent_level: int = 0,
) -> ListFlowable:
    scale = (
        styles["bullet"].fontSize
        / 7.75
    )

    list_indent = (
        11
        + (15 * indent_level)
    ) * scale

    return ListFlowable(
        [
            ListItem(
                Paragraph(
                    _text(item),
                    styles["bullet"],
                ),
                leftIndent=(
                    7
                    + (6 * indent_level)
                ) * scale,
            )
            for item in items
        ],
        bulletType="bullet",
        start="circle",
        leftIndent=list_indent,
        bulletFontName=(
            styles["bullet"].fontName
        ),
        bulletFontSize=4.3 * scale,
        bulletDedent=11 * scale,
        spaceBefore=0.15 * mm * scale,
        spaceAfter=1.25 * mm * scale,
    )


def _experience_block(
    experience: Any,
    styles: dict[str, ParagraphStyle],
) -> list:
    header = Table(
        [
            [
                Paragraph(
                    (
                        f"{_text(experience.job_title)} - "
                        f"{_text(experience.employer)}"
                    ),
                    styles["entry_title"],
                ),
                Paragraph(
                    (
                        f"{_text(experience.start_date)} - "
                        f"{_text(experience.end_date)}"
                    ),
                    styles["entry_date"],
                ),
            ]
        ],
        colWidths=[147 * mm, 45 * mm],
    )

    continuation_header = Table(
        [
            [
                Paragraph(
                    (
                        f"{_text(experience.job_title)} - "
                        f"{_text(experience.employer)} "
                        f"(continued)"
                    ),
                    styles["entry_title"],
                ),
                Paragraph(
                    (
                        f"{_text(experience.start_date)} - "
                        f"{_text(experience.end_date)}"
                    ),
                    styles["entry_date"],
                ),
            ]
        ],
        colWidths=[147 * mm, 45 * mm],
    )

    header_style = TableStyle(
        [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    header.setStyle(
        header_style
    )
    continuation_header.setStyle(
        header_style
    )

    location = Paragraph(
        _text(experience.location),
        styles["meta"],
    )

    continuation_location = Paragraph(
        _text(experience.location),
        styles["meta"],
    )

    header.keepWithNext = 1
    location.keepWithNext = 1
    continuation_header.keepWithNext = 1
    continuation_location.keepWithNext = 1

    rendered_responsibilities = (
        filter_responsibilities(
            experience.responsibilities,
            experience.achievements,
        )
    )

    if not rendered_responsibilities:
        rendered_responsibilities = list(
            experience.responsibilities
        )

    content: list = [
        header,
        location,
        _bullet_list(
            rendered_responsibilities,
            styles,
            indent_level=0,
        ),
    ]

    if experience.achievements:
        achievement_heading = Paragraph(
            "Key achievements",
            styles["small_bold"],
        )
        achievement_heading.keepWithNext = 1

        content.extend(
            [
                achievement_heading,
                _bullet_list(
                    list(
                        experience.achievements
                    ),
                    styles,
                    indent_level=1,
                ),
            ]
        )

    return [
        PTOContainer(
            content,
            header=[
                continuation_header,
                continuation_location,
            ],
        ),
        Spacer(
            1,
            2.2 * mm,
        ),
    ]


def _project_block(
    project: Any,
    styles: dict[str, ParagraphStyle],
) -> KeepTogether:
    elements: list = [
        Paragraph(
            _text(project.name),
            styles["entry_title"],
        ),
        Paragraph(
            _text(project.status),
            styles["meta"],
        ),
        Paragraph(
            _text(project.description),
            styles["small"],
        ),
    ]

    if project.technologies:
        elements.append(
            Paragraph(
                (
                    "<b>Technologies:</b> "
                    + _text(
                        ", ".join(
                            project.technologies
                        )
                    )
                ),
                styles["small"],
            )
        )

    if project.responsibilities:
        elements.append(
            _bullet_list(
                list(
                    project.responsibilities
                ),
                styles,
                indent_level=0,
            )
        )

    if getattr(
        project,
        "outcomes",
        None,
    ):
        elements.extend(
            [
                Paragraph(
                    "Outcomes",
                    styles["small_bold"],
                ),
                _bullet_list(
                    list(
                        project.outcomes
                    ),
                    styles,
                    indent_level=1,
                ),
            ]
        )

    elements.append(
        Spacer(
            1,
            1.25 * mm,
        )
    )

    return KeepTogether(
        elements
    )


def _education_block(
    education: Any,
    styles: dict[str, ParagraphStyle],
) -> KeepTogether:
    return KeepTogether(
        [
            Paragraph(
                _text(education.qualification),
                styles["entry_title"],
            ),
            Paragraph(
                _text(education.institution),
                styles["small"],
            ),
            Paragraph(
                (
                    f"{_text(education.start_date)} - "
                    f"{_text(education.end_date)}"
                ),
                styles["meta"],
            ),
            Spacer(1, 1 * mm),
        ]
    )


def _build_story(
    cv: CVProfile,
    styles: dict[str, ParagraphStyle],
) -> list:
    story: list = [
        Paragraph(
            _text(cv.personal_info.full_name),
            styles["name"],
        ),
        Paragraph(
            " | ".join(
                [
                    _text(cv.personal_info.location),
                    _text(cv.personal_info.phone),
                    _text(cv.personal_info.email),
                    _text(cv.personal_info.linkedin),
                ]
            ),
            styles["contact"],
        ),
        *_section_heading(
            "Professional Summary",
            styles,
        ),
        Paragraph(
            _text(cv.professional_summary),
            styles["body"],
        ),
        *_section_heading(
            "Core Skills",
            styles,
        ),
        Paragraph(
            _text(" | ".join(cv.core_skills)),
            styles["skills"],
        ),
        *_section_heading(
            "Professional Experience",
            styles,
        ),
    ]

    for experience in (
        cv.professional_experience
    ):
        story.extend(
            _experience_block(
                experience,
                styles,
            )
        )

    projects = list(
        cv.projects[
            :PROJECTS_TO_RENDER
        ]
    )

    if projects:
        first_project = projects[0]

        story.append(
            KeepTogether(
                [
                    *_section_heading(
                        "AI & Technical Projects",
                        styles,
                    ),
                    _project_block(
                        first_project,
                        styles,
                    ),
                ]
            )
        )

        for project in projects[1:]:
            story.append(
                _project_block(
                    project,
                    styles,
                )
            )

    if cv.education:
        story.extend(
            _section_heading(
                "Education",
                styles,
            )
        )

        for education in cv.education:
            story.append(
                _education_block(
                    education,
                    styles,
                )
            )

    if cv.languages:
        story.extend(
            _section_heading(
                "Languages",
                styles,
            )
        )

        story.append(
            Paragraph(
                " | ".join(
                    (
                        f"{_text(item.language)}: "
                        f"{_text(item.level)}"
                    )
                    for item in cv.languages
                ),
                styles["small"],
            )
        )

    if cv.tools_and_technologies:
        story.extend(
            _section_heading(
                "Tools and Technologies",
                styles,
            )
        )

        story.append(
            Paragraph(
                _text(
                    " | ".join(
                        cv.tools_and_technologies
                    )
                ),
                styles["small"],
            )
        )

    return story


def _render_once(
    cv: CVProfile,
    *,
    scale: float,
) -> bytes:
    regular_font, bold_font = (
        _register_fonts()
    )

    styles = _build_styles(
        regular_font=regular_font,
        bold_font=bold_font,
        scale=scale,
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=9 * mm,
        rightMargin=9 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
        title=f"{cv.personal_info.full_name} - CV",
        author=cv.personal_info.full_name,
        subject="Tailored CV",
    )

    document.build(
        _build_story(
            cv,
            styles,
        )
    )

    return buffer.getvalue()


def count_pdf_pages(pdf_bytes: bytes) -> int:
    return len(
        PdfReader(
            BytesIO(pdf_bytes)
        ).pages
    )


def generate_cv_pdf(
    cv: CVProfile,
) -> bytes:
    logger.info(
        "CV PDF generation started: profile_id=%s",
        cv.profile_id,
    )

    last_page_count: int | None = None

    try:
        for scale in FONT_SCALE_ATTEMPTS:
            pdf_bytes = _render_once(
                cv,
                scale=scale,
            )

            page_count = count_pdf_pages(
                pdf_bytes
            )

            last_page_count = page_count

            logger.info(
                "CV PDF render attempt completed: "
                "scale=%s pages=%s",
                scale,
                page_count,
            )

            if page_count <= MAX_PDF_PAGES:
                logger.info(
                    "CV PDF generation completed: "
                    "pages=%s scale=%s",
                    page_count,
                    scale,
                )

                return pdf_bytes

        raise PDFRenderError(
            "The generated CV exceeds the two-page limit "
            f"after all layout attempts. Last result: "
            f"{last_page_count} pages."
        )

    except PDFRenderError:
        logger.exception(
            "CV PDF generation failed."
        )
        raise

    except Exception as error:
        logger.exception(
            "Unexpected CV PDF generation failure."
        )

        raise PDFRenderError(
            "The CV PDF could not be generated."
        ) from error


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

generate_cv_pdf = observe_function(
    "pdf_generation"
)(generate_cv_pdf)
