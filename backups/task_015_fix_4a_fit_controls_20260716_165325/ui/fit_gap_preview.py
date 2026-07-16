from __future__ import annotations

from typing import Any

import streamlit as st


def _render_items(
    title: str,
    items: list[Any],
) -> None:
    st.markdown(f"**{title}**")

    if not items:
        st.caption("None listed.")
        return

    for item in items:
        st.write(f"- {item}")


def _render_fit_message(
    level: str,
    explanation: str,
) -> None:
    normalized = level.lower()

    if normalized in {
        "strong",
        "solid",
    }:
        st.success(explanation)

    elif normalized == "stretch":
        st.warning(explanation)

    else:
        st.error(explanation)


def _render_impact_message(
    impact: str,
    requirement: str,
) -> None:
    message = (
        f"{impact.upper()} impact · "
        f"{requirement}"
    )

    if impact == "high":
        st.error(message)

    elif impact == "medium":
        st.warning(message)

    else:
        st.info(message)


def render_fit_and_gap(application) -> None:
    st.subheader("Role fit")

    fit = application.fit_assessment

    metric_column, details_column = (
        st.columns([1, 3])
    )

    with metric_column:
        st.metric(
            "Fit level",
            fit.level.upper(),
        )

    with details_column:
        _render_fit_message(
            fit.level,
            fit.explanation,
        )

    evidence_column, missing_column = (
        st.columns(2)
    )

    with evidence_column:
        with st.container(border=True):
            _render_items(
                "Relevant experience",
                list(
                    fit.relevant_experience
                ),
            )

    with missing_column:
        with st.container(border=True):
            _render_items(
                "Missing requirements",
                list(
                    fit.missing_requirements
                ),
            )

    st.subheader("Gap analysis")

    supported_column, derived_column = (
        st.columns(2)
    )

    with supported_column:
        with st.container(border=True):
            _render_items(
                "Supported requirements",
                list(
                    application
                    .gap_analysis
                    .supported_requirements
                ),
            )

    with derived_column:
        with st.container(border=True):
            _render_items(
                "Reasonably derived",
                list(
                    application
                    .gap_analysis
                    .reasonably_derived_requirements
                ),
            )

    unsupported = list(
        application
        .gap_analysis
        .unsupported_requirements
    )

    st.markdown(
        "#### Unsupported requirements"
    )

    if not unsupported:
        st.success(
            "No unsupported requirements listed."
        )
        return

    impact_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    unsupported.sort(
        key=lambda item: (
            impact_order.get(
                item.impact,
                3,
            )
        )
    )

    for item in unsupported:
        _render_impact_message(
            item.impact,
            item.requirement,
        )

        with st.expander(
            "Preparation and interview guidance",
            expanded=(
                item.impact == "high"
            ),
        ):
            st.markdown(
                "**Preparation recommendation**"
            )
            st.write(
                item.preparation_recommendation
            )

            st.markdown(
                "**Interview guidance**"
            )
            st.write(
                item.interview_guidance
            )
