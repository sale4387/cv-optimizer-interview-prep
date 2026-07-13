from __future__ import annotations

from html import escape

import streamlit as st

from cv_data.models import CVProfile


PROJECTS_TO_RENDER = 3


PRINT_STYLES = """
<style>
@page {
    size: A4;
    margin: 10mm;
}

@media print {
    [data-testid="stSidebar"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stButton"],
    [data-testid="stAlert"],
    iframe,
    .no-print {
        display: none !important;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    .main,
    .block-container {
        margin: 0 !important;
        padding: 0 !important;
        background: #ffffff !important;
        max-width: none !important;
    }

    .cv-entry {
        break-inside: avoid;
        page-break-inside: avoid;
    }
}
</style>
""".strip()


def _text(value: str) -> str:
    return escape(value, quote=True)


def _list_html(items: list[str]) -> str:
    return "".join(
        f"<li>{_text(item)}</li>"
        for item in items
    )


def build_cv_html(
    cv: CVProfile,
) -> str:
    experience_html = "".join(
        (
            '<article class="cv-entry">'
            f"<h3>{_text(item.job_title)} — {_text(item.employer)}</h3>"
            f"<p>{_text(item.location)} | "
            f"{_text(item.start_date)} – {_text(item.end_date)}</p>"
            f"<ul>{_list_html(item.responsibilities)}</ul>"
            "</article>"
        )
        for item in cv.professional_experience
    )

    projects_html = "".join(
        (
            '<article class="cv-entry">'
            f"<h3>{_text(item.name)}</h3>"
            f"<p>{_text(item.description)}</p>"
            "</article>"
        )
        for item in cv.projects[:PROJECTS_TO_RENDER]
    )

    education_html = "".join(
        (
            '<article class="cv-entry">'
            f"<h3>{_text(item.qualification)}</h3>"
            f"<p>{_text(item.institution)} | "
            f"{_text(item.start_date)} – {_text(item.end_date)}</p>"
            "</article>"
        )
        for item in cv.education
    )

    languages = " | ".join(
        f"{_text(item.language)}: {_text(item.level)}"
        for item in cv.languages
    )

    return (
        f"{PRINT_STYLES}"
        '<main class="cv-document">'
        f"<h1>{_text(cv.personal_info.full_name)}</h1>"
        f"<p>{_text(cv.personal_info.location)} | "
        f"{_text(cv.personal_info.phone)} | "
        f"{_text(cv.personal_info.email)}</p>"
        "<h2>Professional Summary</h2>"
        f"<p>{_text(cv.professional_summary)}</p>"
        "<h2>Core Skills</h2>"
        f"<p>{_text(' | '.join(cv.core_skills))}</p>"
        "<h2>Professional Experience</h2>"
        f"{experience_html}"
        "<h2>AI &amp; Technical Projects</h2>"
        f"{projects_html}"
        "<h2>Education</h2>"
        f"{education_html}"
        "<h2>Languages</h2>"
        f"<p>{languages}</p>"
        "<h2>Tools and Technologies</h2>"
        f"<p>{_text(' | '.join(cv.tools_and_technologies))}</p>"
        "</main>"
    )


def _render_bullets(items: list[str]) -> None:
    for item in items:
        st.markdown(f"- {item}")


def render_cv_preview(
    cv: CVProfile,
) -> None:
    st.title(cv.personal_info.full_name)

    st.caption(
        " | ".join(
            [
                cv.personal_info.location,
                cv.personal_info.phone,
                cv.personal_info.email,
            ]
        )
    )

    if cv.personal_info.linkedin:
        st.link_button(
            "LinkedIn",
            cv.personal_info.linkedin,
        )

    st.subheader("Professional Summary")
    st.write(cv.professional_summary)

    st.subheader("Core Skills")
    st.write(" | ".join(cv.core_skills))

    st.subheader("Professional Experience")

    for experience in cv.professional_experience:
        left, right = st.columns([4, 1])

        with left:
            st.markdown(
                f"**{experience.job_title} — {experience.employer}**"
            )

        with right:
            st.caption(
                f"{experience.start_date} – {experience.end_date}"
            )

        st.caption(experience.location)
        _render_bullets(experience.responsibilities)

        if experience.achievements:
            st.markdown("**Key achievements**")
            _render_bullets(experience.achievements)

        st.divider()

    if cv.projects:
        st.subheader("AI & Technical Projects")

        for project in cv.projects[:PROJECTS_TO_RENDER]:
            st.markdown(f"**{project.name}**")
            st.caption(project.status)
            st.write(project.description)

            if project.technologies:
                st.write(
                    "**Technologies:** "
                    + ", ".join(project.technologies)
                )

            if project.responsibilities:
                _render_bullets(project.responsibilities)

            st.divider()

    if cv.education:
        st.subheader("Education")

        for item in cv.education:
            left, right = st.columns([4, 1])

            with left:
                st.markdown(f"**{item.qualification}**")
                st.caption(item.institution)

            with right:
                st.caption(
                    f"{item.start_date} – {item.end_date}"
                )

    if cv.languages:
        st.subheader("Languages")
        st.write(
            " | ".join(
                f"{item.language}: {item.level}"
                for item in cv.languages
            )
        )

    if cv.tools_and_technologies:
        st.subheader("Tools and Technologies")
        st.write(
            " | ".join(cv.tools_and_technologies)
        )
