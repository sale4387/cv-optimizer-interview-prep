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


def _render_fit_level(
    level: str,
) -> None:
    normalized = level.lower()
    label = normalized.upper()

    if normalized in {
        "strong",
        "solid",
    }:
        st.markdown(
            f":green[**{label}**]"
        )

    elif normalized == "stretch":
        st.markdown(
            f":orange[**{label}**]"
        )

    else:
        st.markdown(
            f":red[**{label}**]"
        )


def _escape_currency_markdown(
    value: str,
) -> str:
    return value.replace(
        "$",
        r"\$",
    )


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

    level_column, details_column = (
        st.columns(
            [1, 5],
            gap="small",
        )
    )

    with level_column:
        st.markdown("**Fit level**")
        _render_fit_level(
            fit.level
        )

    with details_column:
        st.markdown("**Assessment**")

        with st.container(
            border=True
        ):
            st.markdown(
                _escape_currency_markdown(
                    fit.explanation
                )
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
