from __future__ import annotations

import re
import sys
from pathlib import Path

import pycountry
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from ui.interview_prep import render_application_interview_prep

from firebase import (
    format_timestamp_amsterdam,
)
from services.application_service import (
    ApplicationResultError,
    SavedApplicationResult,
    create_draft_application,
    list_saved_application_results,
    load_saved_application,
)
from services.company_service import (
    CompanyResearchError,
    list_saved_company_research,
    load_saved_company_research,
)
from services.candidate_profile_service import (
    CandidateProfileError,
    list_candidate_options,
)
from services.revision_service import (
    ApplicationRevisionError,
    DraftPDFExportError,
    EDITABLE_REVISION_SECTIONS,
    accept_saved_application,
    generate_accepted_application_pdf,
    revise_saved_application,
)
from ui.cv_preview import (
    render_cv_preview,
)
from ui.cv_landing import (
    render_cv_landing_page,
)
from ui.inline_review import (
    render_inline_review,
)
from ui.fit_gap_preview import (
    render_fit_and_gap,
)


st.set_page_config(
    page_title="CV Optimizer",
    layout="wide",
)


GLOBAL_STYLES = """
<style>
.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.application-card {
    padding: 16px 18px;
    margin-bottom: 12px;
    border: 1px solid #d8dee7;
    border-radius: 10px;
    background: #ffffff;
}

.application-meta {
    color: #5b6472;
    font-size: 13px;
}
</style>
"""


COUNTRY_NAMES = {
    country.alpha_2: country.name
    for country in pycountry.countries
}

COUNTRY_CODES = sorted(
    COUNTRY_NAMES,
    key=lambda code: COUNTRY_NAMES[
        code
    ],
)

DEFAULT_COUNTRY_INDEX = (
    COUNTRY_CODES.index("NL")
)


def _navigate(
    page: str,
    application_id: (
        str | None
    ) = None,
    company_key: (
        str | None
    ) = None,
) -> None:
    parameters = {
        "page": page,
    }

    if application_id is not None:
        parameters["application_id"] = (
            application_id
        )

    if company_key is not None:
        parameters["company_key"] = (
            company_key
        )

    st.query_params.from_dict(
        parameters
    )


def _queue_toast(
    message: str,
) -> None:
    st.session_state[
        "ui_toast_message"
    ] = message


def _show_pending_toast() -> None:
    message = st.session_state.pop(
        "ui_toast_message",
        None,
    )

    if message:
        st.toast(
            str(message),
            icon="✅",
        )


def _render_sidebar() -> None:
    st.sidebar.title(
        "CV Optimizer"
    )

    if st.sidebar.button(
        "Current CV",
        key="sidebar_current_cv_1",
        width="stretch",
    ):
        st.query_params.from_dict(
            {
                "page": "cv",
                **(
                    {"profile": st.query_params.get("profile")}
                    if st.query_params.get("profile")
                    else {}
                ),
            }
        )
        st.rerun()

    if st.sidebar.button(
        "Optimize CV",
        key="sidebar_optimize_cv_2",
        width="stretch",
    ):
        st.query_params.from_dict(
            {
                "page": "optimize",
                **(
                    {"profile": st.query_params.get("profile")}
                    if st.query_params.get("profile")
                    else {}
                ),
            }
        )
        st.rerun()

    if st.sidebar.button(
        "My Applications",
        key="sidebar_my_applications_1",
        width="stretch",
    ):
        _navigate("applications")
        st.rerun()

    if st.sidebar.button(
        "Companies",
        key="sidebar_companies_1",
        width="stretch",
    ):
        _navigate("companies")
        st.rerun()


def _render_optimize_page() -> None:
    st.title("Optimize CV")

    st.caption(
        "Paste a job ad and create a "
        "validated, saved CV result."
    )

    try:
        candidate_options = (
            list_candidate_options()
        )

    except CandidateProfileError as error:
        st.error(str(error))
        return

    with st.form(
        "cv_optimization_form"
    ):
        requested_profile_id = (
            st.query_params.get("profile")
        )

        default_profile_index = 0

        for index, option in enumerate(
            candidate_options
        ):
            if (
                option.profile_id
                == requested_profile_id
            ):
                default_profile_index = index
                break

        selected_candidate = st.selectbox(
            "Candidate profile",
            options=candidate_options,
            index=default_profile_index,
            format_func=lambda option: (
                option.display_name
            ),
        )

        job_title = st.text_input(
            "Job title",
            max_chars=200,
        )

        company_name_input = (
            st.text_input(
                "Company name",
                max_chars=200,
            )
        )

        country_code = st.selectbox(
            "Country",
            options=COUNTRY_CODES,
            index=(
                DEFAULT_COUNTRY_INDEX
            ),
            format_func=lambda code: (
                f"{COUNTRY_NAMES[code]} "
                f"({code})"
            ),
        )

        company_name = (
            f"{company_name_input.strip()}"
            f" - {country_code}"
        )

        job_ad_text = st.text_area(
            "Job advertisement",
            height=340,
            max_chars=50000,
        )

        submitted = (
            st.form_submit_button(
                "Optimize CV",
                type="primary",
                width="stretch",
            )
        )

    if not submitted:
        return

    try:
        with st.spinner(
            "Analyzing fit, tailoring "
            "the CV and saving the result..."
        ):
            saved_result = (
                create_draft_application(
                    job_title=job_title,
                    company_name=(
                        company_name
                    ),
                    job_ad_text=(
                        job_ad_text
                    ),
                    profile_path=(
                        selected_candidate
                        .cv_path
                    ),
                )
            )

        _queue_toast(
            "CV optimization completed."
        )

        _navigate(
            "preview",
            saved_result.application_id,
        )

        st.rerun()

    except ValueError as error:
        st.error(str(error))

    except ApplicationResultError as error:
        st.error(str(error))

    except Exception:
        st.error(
            "The CV result could "
            "not be created."
        )


def _render_poor_fit(
    application: (
        SavedApplicationResult
    ),
) -> None:
    st.warning(
        "CV tailoring stopped because "
        "the role fit is poor."
    )

    render_fit_and_gap(
        application
    )


def _revision_key(
    application_id: str,
    name: str,
) -> str:
    return (
        f"revision_{application_id}_"
        f"{name}"
    )


def _clear_revision_state(
    application_id: str,
) -> None:
    names = [
        "active",
        "success",
    ]

    for section in (
        EDITABLE_REVISION_SECTIONS
    ):
        names.extend(
            [
                f"{section}_selected",
                f"{section}_comment",
            ]
        )

    for name in names:
        st.session_state.pop(
            _revision_key(
                application_id,
                name,
            ),
            None,
        )


def _render_revision_editor(
    application: (
        SavedApplicationResult
    ),
) -> None:
    application_id = (
        application.application_id
    )

    st.subheader(
        "Request changes"
    )

    st.caption(
        "Select only the sections you "
        "want to revise and describe "
        "the required change."
    )

    comments: dict[str, str] = {}

    for (
        section,
        label,
    ) in (
        EDITABLE_REVISION_SECTIONS
        .items()
    ):
        selected_key = (
            _revision_key(
                application_id,
                f"{section}_selected",
            )
        )

        comment_key = (
            _revision_key(
                application_id,
                f"{section}_comment",
            )
        )

        selected = st.checkbox(
            label,
            key=selected_key,
        )

        comment = st.text_area(
            f"Comment for {label}",
            key=comment_key,
            disabled=not selected,
            height=100,
            placeholder=(
                "Describe what should "
                "change in this section."
            ),
        )

        if selected:
            comments[section] = (
                comment
            )

    cancel_column, change_column = (
        st.columns(2)
    )

    with cancel_column:
        if st.button(
            "Cancel",
            key=_revision_key(
                application_id,
                "cancel",
            ),
            width="stretch",
        ):
            _clear_revision_state(
                application_id
            )

            st.rerun()

    with change_column:
        if st.button(
            "Make changes",
            key=_revision_key(
                application_id,
                "submit",
            ),
            type="primary",
            width="stretch",
        ):
            try:
                with st.spinner(
                    "Revising selected "
                    "CV sections..."
                ):
                    revise_saved_application(
                        application_id=(
                            application_id
                        ),
                        comments=comments,
                    )

                _clear_revision_state(
                    application_id
                )

                st.session_state[
                    _revision_key(
                        application_id,
                        "success",
                    )
                ] = True

                st.rerun()

            except (
                ValueError,
                ApplicationRevisionError,
            ) as error:
                st.error(str(error))

            except Exception:
                st.error(
                    "The requested changes "
                    "could not be saved."
                )


def _safe_pdf_name(
    job_title: str,
) -> str:
    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        job_title.strip(),
    ).strip("-")

    return (
        safe_name
        or "tailored-cv"
    )


def _render_accepted_download(
    application: (
        SavedApplicationResult
    ),
) -> None:
    st.success(
        "CV accepted"
    )

    try:
        pdf_bytes = (
            generate_accepted_application_pdf(
                application
            )
        )

        st.download_button(
            label=(
                "Download CV as PDF"
            ),
            data=pdf_bytes,
            file_name=(
                f"{_safe_pdf_name(
                    application.job_title
                )}.pdf"
            ),
            mime="application/pdf",
            type="primary",
            width="stretch",
        )

    except (
        DraftPDFExportError,
        ApplicationRevisionError,
    ) as error:
        st.error(str(error))

    except Exception:
        st.error(
            "The PDF could not "
            "be generated."
        )


def _render_review_controls(
    application: (
        SavedApplicationResult
    ),
    *,
    review_ready: bool,
) -> None:
    if application.tailored_cv is None:
        st.info(
            "Review controls are available only when the application contains a tailored CV."
        )
        return

    if application.status != "draft":
        return

    application_id = (
        application.application_id
    )

    success_key = _revision_key(
        application_id,
        "success",
    )

    if st.session_state.pop(
        success_key,
        False,
    ):
        st.toast(
            "The selected sections "
            "were updated.",
            icon="✅",
        )

    st.caption(
        "Use Inline CV review above to accept, keep or request revisions. "
        "Accept the CV when the review is complete."
    )

    if not review_ready:
        st.warning(
            "Save and resolve all inline review "
            "decisions before accepting the CV."
        )

    if st.button(
        "Accept CV",
        key=_revision_key(
            application_id,
            "accept",
        ),
        type="primary",
        width="stretch",
        disabled=not review_ready,
    ):
        try:
            with st.spinner(
                "Accepting CV..."
            ):
                accept_saved_application(
                    application_id
                )

            st.rerun()

        except (
            ApplicationRevisionError
        ) as error:
            st.error(str(error))

    st.info(
        "Accept the CV to enable "
        "PDF download."
    )


def _preview_section_key(
    application_id: str,
    section_name: str,
) -> str:
    return (
        f"preview_section_"
        f"{application_id}_"
        f"{section_name}"
    )


def _workflow_status_label(
    value: object,
) -> str:
    normalized = str(
        value
        or "not_started"
    ).replace(
        "_",
        " ",
    )

    return normalized.title()


def _render_section_toggle(
    *,
    application_id: str,
    section_name: str,
    title: str,
    summary: str,
    default_open: bool,
) -> bool:
    with st.container(
        border=True
    ):
        title_column, toggle_column = (
            st.columns(
                [5, 1]
            )
        )

        with title_column:
            st.markdown(
                f"### {title}"
            )
            st.caption(
                summary
            )

        with toggle_column:
            is_open = st.toggle(
                "Open",
                value=default_open,
                key=(
                    _preview_section_key(
                        application_id,
                        section_name,
                    )
                ),
            )

    return is_open


def _render_preview_page() -> None:
    application_id = (
        st.query_params.get(
            "application_id"
        )
    )

    st.title("CV Preview")

    if not application_id:
        st.error(
            "No application ID "
            "was provided."
        )
        return

    try:
        application = (
            load_saved_application(
                application_id
            )
        )

    except ApplicationResultError as error:
        st.error(str(error))
        return

    if application is None:
        st.warning(
            "The requested application "
            "does not exist."
        )
        return

    st.caption(
        f"{application.profile_id} · "
        f"{application.job_title} · "
        f"{application.company_key} · "
        f"{application.status}"
    )

    if application.tailored_cv is None:
        _render_poor_fit(
            application
        )
        return

    if application.status == "accepted":
        _render_accepted_download(
            application
        )

        st.divider()

    workflow_status = dict(
        application.workflow_status
        or {}
    )

    fit_summary = (
        "Fit level: "
        f"{application.fit_assessment.level.upper()} "
        "· requirements, evidence, gaps "
        "and preparation advice"
    )

    cv_summary = (
        "Accepted CV · PDF available"
        if application.status
        == "accepted"
        else (
            "Draft CV · review decisions, "
            "preview and acceptance"
        )
    )

    interview_status = (
        _workflow_status_label(
            workflow_status.get(
                "interview_prep"
            )
        )
    )

    interview_summary = (
        "Status: "
        f"{interview_status} · "
        "application-specific questions, "
        "evidence and answer guidance"
    )

    fit_open = _render_section_toggle(
        application_id=(
            application.application_id
        ),
        section_name="fit_gap",
        title=(
            "1. Fit, gap and "
            "requirements"
        ),
        summary=fit_summary,
        default_open=False,
    )

    if fit_open:
        with st.container(
            border=True
        ):
            render_fit_and_gap(
                application
            )

    cv_open = _render_section_toggle(
        application_id=(
            application.application_id
        ),
        section_name="tailored_cv",
        title="2. Tailored CV",
        summary=cv_summary,
        default_open=(
            application.status
            == "draft"
        ),
    )

    if cv_open:
        with st.container(
            border=True
        ):
            review_ready = True

            if (
                application.status
                == "draft"
            ):
                review_ready = (
                    render_inline_review(
                        application
                    )
                )

                st.divider()

            render_cv_preview(
                application.tailored_cv
            )

            if (
                application.status
                == "draft"
            ):
                st.divider()

                _render_review_controls(
                    application,
                    review_ready=(
                        review_ready
                    ),
                )

    interview_open = (
        _render_section_toggle(
            application_id=(
                application.application_id
            ),
            section_name=(
                "interview_prep"
            ),
            title=(
                "3. Interview preparation"
            ),
            summary=(
                interview_summary
            ),
            default_open=False,
        )
    )

    if interview_open:
        with st.container(
            border=True
        ):
            try:
                render_application_interview_prep(
                    application
                )

            except Exception as error:
                st.warning(
                    "Interview preparation "
                    "is unavailable: "
                    f"{error}"
                )


def _render_application_card(
    application: (
        SavedApplicationResult
    ),
    index: int,
) -> None:
    created_at = (
        format_timestamp_amsterdam(
            application.created_at,
            "%d %b %Y, %H:%M",
        )
    )

    left, right = st.columns(
        [5, 1]
    )

    with left:
        st.markdown(
            f"**{application.job_title}**"
        )

        st.caption(
            f"{application.profile_id} · "
            f"{application.company_key} · "
            f"{created_at} · "
            f"{application.status}"
        )

    with right:
        if st.button(
            "Open",
            key=(
                "open_application_"
                f"{index}_"
                f"{application.application_id}"
            ),
            width="stretch",
        ):
            _navigate(
                "preview",
                application
                .application_id,
            )

            st.rerun()

    st.divider()


def _render_applications_page() -> None:
    st.title(
        "My Applications"
    )

    st.caption(
        "Saved applications are shown "
        "from newest to oldest."
    )

    try:
        applications = (
            list_saved_application_results()
        )

    except ApplicationResultError as error:
        st.error(str(error))
        return

    if not applications:
        st.info(
            "No saved applications "
            "were found."
        )
        return

    for (
        index,
        application,
    ) in enumerate(applications):
        _render_application_card(
            application,
            index,
        )



def _render_company_report(
    company,
) -> None:
    report = company.company_research

    st.title(report.display_name)

    status_column, confidence_column, industry_column = (
        st.columns(3)
    )

    with status_column:
        st.metric(
            "Research status",
            report.research_status.title(),
        )

    with confidence_column:
        st.metric(
            "Confidence",
            report.confidence_level.title(),
        )

    with industry_column:
        st.metric(
            "Primary industry",
            report.industry.primary_industry,
        )

    st.caption(
        f"{report.company_key} · "
        f"valid until "
        f"{report.valid_until.date()}"
    )

    st.divider()

    with st.expander(
        "1. Company overview",
        expanded=False,
    ):
        st.markdown(
            "#### Overview"
        )
        st.write(
            report.short_description
        )

        st.markdown(
            "#### Industry and business model"
        )
        st.write(
            report.industry.business_model
        )

        if (
            report.industry
            .secondary_industries
        ):
            st.markdown(
                "**Related industries**"
            )

            for industry in (
                report.industry
                .secondary_industries
            ):
                st.write(
                    f"- {industry}"
                )

    with st.expander(
        "2. Products and services",
        expanded=False,
    ):
        for item in (
            report.products_and_services
        ):
            st.markdown(
                f"#### {item.name}"
            )
            st.caption(
                item.type.title()
            )
            st.write(
                item.description
            )
            st.markdown(
                "**Interview relevance**"
            )
            st.write(
                item
                .why_it_matters_for_interview
            )
            st.divider()

    with st.expander(
        "3. Customers and market",
        expanded=False,
    ):
        st.markdown(
            "#### Known public customers"
        )

        known_customers = (
            report.customers_and_market
            .known_public_customers
        )

        if known_customers:
            for customer in (
                known_customers
            ):
                st.markdown(
                    f"**{customer.name}**"
                )
                st.write(
                    customer.context
                )

        else:
            st.caption(
                "No verified public customers listed."
            )

        st.markdown(
            "#### Customer types"
        )

        customer_types = (
            report.customers_and_market
            .customer_types
        )

        if customer_types:
            for customer_type in (
                customer_types
            ):
                st.write(
                    f"- {customer_type}"
                )

        else:
            st.caption(
                "No customer types listed."
            )

        st.markdown(
            "#### Target markets"
        )

        target_markets = (
            report.customers_and_market
            .target_markets
        )

        if target_markets:
            for target_market in (
                target_markets
            ):
                st.write(
                    f"- {target_market}"
                )

        else:
            st.caption(
                "No target markets listed."
            )

        limitations = (
            report.customers_and_market
            .limitations
        )

        if limitations:
            st.info(
                limitations
            )

    with st.expander(
        "4. Competitors",
        expanded=False,
    ):
        for competitor in (
            report.competitors
        ):
            st.markdown(
                f"#### {competitor.name}"
            )
            st.write(
                competitor.reason
            )

            if competitor.comparison_note:
                st.caption(
                    competitor.comparison_note
                )

            st.divider()

    with st.expander(
        "5. Recent developments",
        expanded=False,
    ):
        if report.recent_developments:
            for development in (
                report.recent_developments
            ):
                st.markdown(
                    f"#### {development.title}"
                )
                st.caption(
                    f"{development.date} · "
                    f"{development.type}"
                )
                st.write(
                    development.summary
                )
                st.markdown(
                    "**Interview relevance**"
                )
                st.write(
                    development
                    .interview_relevance
                )
                st.divider()

        else:
            st.caption(
                "No recent developments listed."
            )

    with st.expander(
        "6. Interview intelligence",
        expanded=False,
    ):
        talking_points = (
            report.interview_intelligence
            .talking_points
        )

        st.markdown(
            "#### Company talking points"
        )

        if talking_points:
            for point in (
                talking_points
            ):
                st.markdown(
                    f"**{point.topic}**"
                )
                st.write(
                    point.why_it_matters
                )
                st.markdown(
                    "**How to use it**"
                )
                st.write(
                    point.how_to_use
                )
                st.divider()

        else:
            st.caption(
                "No talking points listed."
            )

        risks = (
            report.interview_intelligence
            .risks_to_prepare_for
        )

        st.markdown(
            "#### Company-related risks"
        )

        if risks:
            for risk in risks:
                st.markdown(
                    f"**{risk.risk}**"
                )
                st.write(
                    risk.preparation_note
                )

        else:
            st.caption(
                "No company-related risks listed."
            )

    with st.expander(
        "7. Employee and public company signals",
        expanded=False,
    ):
        st.markdown(
            "#### Employee sentiment"
        )
        st.markdown(
            "**Public signal:** "
            + (
                report.employee_sentiment
                .signal
                .replace(
                    "_",
                    " ",
                )
                .title()
            )
        )
        st.write(
            report.employee_sentiment
            .summary
        )
        st.markdown(
            "**Interview caution**"
        )
        st.write(
            report.employee_sentiment
            .interview_caution
        )

        if (
            report.employee_sentiment
            .positive_themes
        ):
            st.markdown(
                "**Positive themes**"
            )

            for theme in (
                report.employee_sentiment
                .positive_themes
            ):
                st.write(
                    f"- {theme}"
                )

        if (
            report.employee_sentiment
            .negative_themes
        ):
            st.markdown(
                "**Negative themes**"
            )

            for theme in (
                report.employee_sentiment
                .negative_themes
            ):
                st.write(
                    f"- {theme}"
                )

        if (
            report.employee_sentiment
            .limitations
        ):
            st.info(
                report.employee_sentiment
                .limitations
            )

        st.divider()

        st.markdown(
            "#### Public company information"
        )

        public_info = (
            report.public_company_information
        )

        if public_info.is_public_company:
            st.write(
                f"Ticker: "
                f"{public_info.ticker or 'Not listed'}"
            )
            st.write(
                f"Exchange: "
                f"{public_info.exchange or 'Not listed'}"
            )

        else:
            st.write(
                "The company is not marked "
                "as publicly listed."
            )

        if public_info.summary:
            st.write(
                public_info.summary
            )

        if public_info.limitations:
            st.caption(
                public_info.limitations
            )

    with st.expander(
        "8. Sources and limitations",
        expanded=False,
    ):
        st.markdown(
            "#### Research limitations"
        )

        if report.limitations:
            for limitation in (
                report.limitations
            ):
                st.warning(
                    limitation
                )

        else:
            st.caption(
                "No report-level limitations listed."
            )

        st.markdown(
            "#### Sources"
        )

        if report.sources:
            for source in (
                report.sources
            ):
                st.markdown(
                    f"- [{source.title}]"
                    f"({source.url}) — "
                    f"{source.publisher}"
                )

        else:
            st.caption(
                "No sources listed."
            )


def _render_company_preview_page() -> None:
    company_key = st.query_params.get(
        "company_key"
    )

    if not company_key:
        st.error(
            "No company key was provided."
        )
        return

    try:
        company = load_saved_company_research(
            company_key
        )

    except CompanyResearchError as error:
        st.error(str(error))
        return

    if company is None:
        st.warning(
            "The requested company report does not exist."
        )
        return

    _render_company_report(company)


def _render_companies_page() -> None:
    st.title("Companies")

    st.caption(
        "Saved company reports are shown from newest to oldest."
    )

    try:
        companies = list_saved_company_research()

    except CompanyResearchError as error:
        st.error(str(error))
        return

    if not companies:
        st.info(
            "No saved company reports were found."
        )
        return

    for index, company in enumerate(companies):
        left, right = st.columns([5, 1])

        with left:
            st.markdown(
                f"**{company.display_name}**"
            )

            st.caption(
                f"{company.company_key} · "
                f"{company.company_research.research_status} · "
                f"valid until "
                f"{company.company_research.valid_until.date()}"
            )

        with right:
            if st.button(
                "Open",
                key=(
                    "open_company_"
                    f"{index}_"
                    f"{company.company_key}"
                ),
                width="stretch",
            ):
                _navigate(
                    "company",
                    company_key=(
                        company.company_key
                    ),
                )

                st.rerun()

        st.divider()

def main() -> None:
    st.markdown(
        GLOBAL_STYLES,
        unsafe_allow_html=True,
    )

    _render_sidebar()
    _show_pending_toast()

    page = st.query_params.get(
        "page",
        "cv",
    )

    if page == "cv":
        render_cv_landing_page()

    elif page == "optimize":
        _render_optimize_page()

    elif page == "preview":
        _render_preview_page()

    elif page == "applications":
        _render_applications_page()

    elif page == "companies":
        _render_companies_page()

    elif page == "company":
        _render_company_preview_page()

    else:
        render_cv_landing_page()


if __name__ == "__main__":
    main()
