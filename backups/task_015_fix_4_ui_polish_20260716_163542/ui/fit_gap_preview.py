from __future__ import annotations

from typing import Any

import streamlit as st


def _render_items(title: str, items: list[Any]) -> None:
    st.markdown(f"**{title}**")

    if not items:
        st.caption("None listed.")
        return

    for item in items:
        st.write(f"- {item}")


def render_fit_and_gap(application) -> None:
    st.subheader("Fit assessment")

    fit = application.fit_assessment

    st.markdown(f"**Level:** {fit.level}")
    st.write(fit.explanation)

    _render_items("Relevant experience", list(fit.relevant_experience))
    _render_items("Missing requirements", list(fit.missing_requirements))

    st.subheader("Gap analysis")

    gap = application.gap_analysis

    _render_items("Supported requirements", list(gap.supported_requirements))
    _render_items("Reasonably derived requirements", list(gap.reasonably_derived_requirements))

    st.markdown("**Unsupported requirements**")

    if not gap.unsupported_requirements:
        st.caption("None listed.")
        return

    for item in gap.unsupported_requirements:
        with st.expander(f"{item.requirement} · impact: {item.impact}"):
            st.markdown("**Preparation recommendation**")
            st.write(item.preparation_recommendation)

            st.markdown("**Interview guidance**")
            st.write(item.interview_guidance)
