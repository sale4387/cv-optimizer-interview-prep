import json
import sys
from html import escape
from pathlib import Path

import streamlit as st
from pydantic import ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cv_data.models import CVProfile


CV_FILE = PROJECT_ROOT / "cv_data" / "cv_sale.json"
PROJECTS_TO_RENDER = 3


def load_cv() -> CVProfile:
    try:
        cv_data = json.loads(CV_FILE.read_text(encoding="utf-8"))
        return CVProfile.model_validate(cv_data)
    except FileNotFoundError:
        st.error("CV data file was not found.")
        st.stop()
    except json.JSONDecodeError:
        st.error("CV data file contains invalid JSON.")
        st.stop()
    except ValidationError:
        st.error("CV data file does not match the expected structure.")
        st.stop()
    except OSError:
        st.error("CV data file could not be read.")
        st.stop()


def text(value: str) -> str:
    return escape(value, quote=True)


def list_html(items: list[str]) -> str:
    return "".join(f"<li>{text(item)}</li>" for item in items)


def build_experience_html(cv: CVProfile) -> str:
    entries: list[str] = []

    for experience in cv.professional_experience:
        achievements_html = ""

        if experience.achievements:
            achievements_html = f"""
                <div class="achievements-block">
                    <div class="sub-label">Key achievements</div>
                    <ul>{list_html(experience.achievements)}</ul>
                </div>
            """

        entries.append(
            f"""
            <section class="experience-entry">
                <div class="entry-heading">
                    <div class="entry-title">
                        {text(experience.job_title)} - {text(experience.employer)}
                    </div>
                    <div class="entry-meta">
                        {text(experience.location)} | {text(experience.start_date)} - {text(experience.end_date)}
                    </div>
                </div>
                <ul>{list_html(experience.responsibilities)}</ul>
                {achievements_html}
            </section>
            """
        )

    return "".join(entries)


def build_projects_html(cv: CVProfile) -> str:
    entries: list[str] = []

    for project in cv.projects[:PROJECTS_TO_RENDER]:
        outcomes_html = ""

        if project.outcomes:
            outcomes_html = f"""
                <div class="project-outcomes">
                    <div class="sub-label">Outcomes</div>
                    <ul>{list_html(project.outcomes)}</ul>
                </div>
            """

        entries.append(
            f"""
            <section class="project-entry">
                <div class="entry-title">{text(project.name)}</div>
                <div class="entry-meta">{text(project.status)}</div>
                <p>{text(project.description)}</p>
                <p><strong>Technologies:</strong> {text(", ".join(project.technologies))}</p>
                <ul>{list_html(project.responsibilities)}</ul>
                {outcomes_html}
            </section>
            """
        )

    return "".join(entries)


def build_education_html(cv: CVProfile) -> str:
    return "".join(
        f"""
        <div class="education-entry">
            <div class="entry-title">{text(item.qualification)}</div>
            <div>{text(item.institution)}</div>
            <div class="entry-meta">{text(item.start_date)} - {text(item.end_date)}</div>
        </div>
        """
        for item in cv.education
    )


def build_cv_html(cv: CVProfile) -> str:
    contact_items = [
        text(cv.personal_info.location),
        text(cv.personal_info.phone),
        f'<a href="mailto:{text(cv.personal_info.email)}">{text(cv.personal_info.email)}</a>',
        f'<a href="{text(cv.personal_info.linkedin)}" target="_blank">LinkedIn</a>',
    ]

    languages = " <span class=\"separator\">|</span> ".join(
        f"<strong>{text(item.language)}:</strong> {text(item.level)}"
        for item in cv.languages
    )

    return f"""
    <article class="cv-document">
        <header class="cv-header">
            <h1>{text(cv.personal_info.full_name)}</h1>
            <div class="contact-line">{" <span class='separator'>|</span> ".join(contact_items)}</div>
        </header>

        <h2>Professional Summary</h2>
        <p>{text(cv.professional_summary)}</p>

        <h2>Core Skills</h2>
        <div class="inline-list">{text(" | ".join(cv.core_skills))}</div>

        <h2>Professional Experience</h2>
        {build_experience_html(cv)}

        <h2>AI &amp; Technical Projects</h2>
        {build_projects_html(cv)}

        <h2>Education</h2>
        <div class="education-list">{build_education_html(cv)}</div>

        <h2>Languages</h2>
        <div class="inline-list">{languages}</div>

        <h2>Tools and Technologies</h2>
        <div class="inline-list">{text(" | ".join(cv.tools_and_technologies))}</div>
    </article>
    """


st.set_page_config(
    page_title="CV Preview",
    layout="centered",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 920px;
            padding: 1rem;
        }

        .cv-document {
            background: #ffffff;
            color: #1f2937;
            padding: 1.4rem 1.6rem;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 0.9rem;
            line-height: 1.28;
            box-shadow: 0 1px 8px rgba(0, 0, 0, 0.14);
        }

        .cv-document h1 {
            color: #111827;
            font-size: 1.75rem;
            line-height: 1.05;
            margin: 0 0 0.35rem 0;
        }

        .cv-document h2 {
            color: #1f2937;
            font-size: 1.08rem;
            line-height: 1.1;
            margin: 0.75rem 0 0.28rem 0;
            padding-bottom: 0.08rem;
            border-bottom: 1px solid #d1d5db;
            break-after: avoid-page;
            page-break-after: avoid;
        }

        .cv-document p {
            margin: 0.08rem 0 0.2rem 0;
        }

        .cv-document ul {
            margin: 0.08rem 0 0.22rem 1.15rem;
            padding-left: 0.3rem;
        }

        .cv-document li {
            margin: 0;
            padding: 0;
            line-height: 1.22;
        }

        .cv-document a {
            color: #0b63b6;
            text-decoration: underline;
        }

        .cv-header {
            margin-bottom: 0.2rem;
        }

        .contact-line,
        .inline-list {
            line-height: 1.3;
        }

        .separator {
            color: #6b7280;
            padding: 0 0.1rem;
        }

        .experience-entry {
            margin-bottom: 0.42rem;
        }

        .entry-heading {
            break-inside: avoid-page;
            page-break-inside: avoid;
            break-after: avoid-page;
            page-break-after: avoid;
        }

        .entry-title {
            color: #111827;
            font-size: 0.93rem;
            font-weight: 700;
            line-height: 1.18;
        }

        .entry-meta {
            color: #6b7280;
            font-size: 0.76rem;
            line-height: 1.2;
            margin: 0.05rem 0 0.08rem 0;
        }

        .achievements-block,
        .project-outcomes {
            margin: 0.18rem 0 0.1rem 0.85rem;
            break-inside: avoid-page;
            page-break-inside: avoid;
        }

        .sub-label {
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.02rem;
        }

        .project-entry {
            margin-bottom: 0.42rem;
            break-inside: avoid-page;
            page-break-inside: avoid;
        }

        .education-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.55rem;
        }

        .education-entry {
            break-inside: avoid-page;
            page-break-inside: avoid;
        }

        @media print {
            @page {
                size: A4;
                margin: 8mm 10mm;
            }

            header,
            footer,
            [data-testid="stToolbar"],
            [data-testid="stSidebar"],
            [data-testid="stDecoration"],
            [data-testid="stStatusWidget"] {
                display: none !important;
            }

            html,
            body,
            [data-testid="stAppViewContainer"] {
                background: #ffffff !important;
            }

            .block-container {
                max-width: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            .cv-document {
                padding: 0 !important;
                box-shadow: none !important;
                font-size: 8.35pt !important;
                line-height: 1.16 !important;
            }

            .cv-document h1 {
                font-size: 17pt !important;
                margin-bottom: 2.5pt !important;
            }

            .cv-document h2 {
                font-size: 10.5pt !important;
                margin: 5pt 0 1.8pt 0 !important;
                padding-bottom: 0.5pt !important;
            }

            .cv-document p,
            .cv-document li,
            .contact-line,
            .inline-list {
                font-size: 8.35pt !important;
                line-height: 1.16 !important;
            }

            .cv-document ul {
                margin: 0.5pt 0 1.7pt 10pt !important;
                padding-left: 4pt !important;
            }

            .experience-entry,
            .project-entry {
                margin-bottom: 3pt !important;
            }

            .entry-title {
                font-size: 8.8pt !important;
            }

            .entry-meta {
                font-size: 7.4pt !important;
                margin: 0.2pt 0 0.7pt 0 !important;
            }

            .sub-label {
                font-size: 7.8pt !important;
            }

            .achievements-block,
            .project-outcomes {
                margin: 1pt 0 0.5pt 8pt !important;
            }

            .education-list {
                gap: 6pt !important;
            }

            .cv-document a {
                color: #111827 !important;
                text-decoration: none !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

cv = load_cv()
st.html(build_cv_html(cv))