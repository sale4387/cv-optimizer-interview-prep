from __future__ import annotations

import re
import sys
from pathlib import Path

import pycountry
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
from ui.interview_prep import render_application_interview_prep
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


def _dismiss_success_dialog() -> None:
    st.session_state[
        "show_success_modal"
    ] = False


@st.dialog(
    "CV optimization completed",
    on_dismiss=_dismiss_success_dialog,
)
def _show_success_dialog(
    application_id: str,
) -> None:
    st.write(
        "CV optimization completed"
    )

    if st.button(
        "Check it now",
        type="primary",
        width="stretch",
    ):
        st.session_state[
            "show_success_modal"
        ] = False

        _navigate(
            "preview",
            application_id,
        )

        st.rerun()


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

    if submitted:
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

            st.session_state[
                "latest_application_id"
            ] = (
                saved_result
                .application_id
            )

            st.session_state[
                "show_success_modal"
            ] = True

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

    if st.session_state.get(
        "show_success_modal",
        False,
    ):
        application_id = (
            st.session_state.get(
                "latest_application_id"
            )
        )

        if application_id:
            _show_success_dialog(
                application_id
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


def _render_review_controls(
    application: (
        SavedApplicationResult
    ),
) -> None:
    if application.tailored_cv is None:
        st.info(
            "Request changes is available only when the application contains a tailored CV."
        )
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
        st.success(
            "The selected sections "
            "were updated. The CV "
            "remains in draft status."
        )

    active_key = _revision_key(
        application_id,
        "active",
    )

    if application.status == "draft":
        request_column, accept_column = (
            st.columns(2)
        )

        with request_column:
            if st.button(
                "Request changes",
                key=_revision_key(
                    application_id,
                    "request",
                ),
                width="stretch",
            ):
                st.session_state[
                    active_key
                ] = True

                st.rerun()

        with accept_column:
            if st.button(
                "Accept CV",
                key=_revision_key(
                    application_id,
                    "accept",
                ),
                type="primary",
                width="stretch",
            ):
                try:
                    with st.spinner(
                        "Accepting CV..."
                    ):
                        (
                            accept_saved_application(
                                application_id
                            )
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

        if st.session_state.get(
            active_key,
            False,
        ):
            _render_revision_editor(
                application
            )

        return

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

    render_fit_and_gap(
        application
    )

    st.divider()

    render_inline_review(
    # TASK-015 FIX-1: application-level interview preparation
    try:
        render_application_interview_prep(application)
    except Exception as exc:
        st.warning(f"Interview preparation is unavailable: {exc}")

        application
    )

    st.divider()

    _render_review_controls(
        application
    )

    st.divider()

    render_cv_preview(
        application.tailored_cv
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

    st.caption(
        f"{report.company_key} · "
        f"{report.research_status} · "
        f"confidence: {report.confidence_level}"
    )

    st.subheader("Short description")
    st.write(report.short_description)

    st.subheader("Industry")
    st.write(report.industry.primary_industry)
    st.caption(report.industry.business_model)

    st.subheader("Products and services")
    for item in report.products_and_services:
        st.markdown(f"**{item.name}**")
        st.write(item.description)
        st.caption(item.why_it_matters_for_interview)

    st.subheader("Customers and market")
    if report.customers_and_market.known_public_customers:
        st.markdown("**Known public customers**")
        for customer in report.customers_and_market.known_public_customers:
            st.write(f"- {customer.name}: {customer.context}")

    if report.customers_and_market.customer_types:
        st.markdown("**Customer types**")
        for customer_type in report.customers_and_market.customer_types:
            st.write(f"- {customer_type}")

    if report.customers_and_market.limitations:
        st.info(report.customers_and_market.limitations)

    st.subheader("Competitors")
    for competitor in report.competitors:
        st.write(f"- **{competitor.name}** — {competitor.reason}")

    if report.recent_developments:
        st.subheader("Recent developments")
        for development in report.recent_developments:
            st.markdown(f"**{development.title}**")
            st.caption(f"{development.date} · {development.type}")
            st.write(development.summary)
            st.caption(development.interview_relevance)

    st.subheader("Interview intelligence")
    st.markdown("**Talking points**")
    for point in report.interview_intelligence.talking_points:
        st.write(f"- **{point.topic}** — {point.how_to_use}")

    st.markdown("**Questions to ask**")
    for question in report.interview_intelligence.questions_to_ask:
        st.write(f"- {question.question}")

    if report.interview_intelligence.risks_to_prepare_for:
        st.markdown("**Risks to prepare for**")
        for risk in report.interview_intelligence.risks_to_prepare_for:
            st.write(f"- **{risk.risk}** — {risk.preparation_note}")

    st.subheader("Employee sentiment")
    st.write(report.employee_sentiment.summary)
    st.caption(report.employee_sentiment.interview_caution)

    if report.limitations:
        st.subheader("Limitations")
        for limitation in report.limitations:
            st.write(f"- {limitation}")

    st.subheader("Sources")
    for source in report.sources:
        st.write(f"- {source.title} — {source.url}")


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
