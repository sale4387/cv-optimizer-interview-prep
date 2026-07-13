from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from ai.interview_prep_models import (
    InterviewPreparationReport,
)


def _as_report(
    interview_prep: (
        InterviewPreparationReport
        | Mapping[str, Any]
    ),
) -> InterviewPreparationReport:
    if isinstance(
        interview_prep,
        InterviewPreparationReport,
    ):
        return interview_prep

    return InterviewPreparationReport.model_validate(
        interview_prep
    )


def render_interview_preparation(
    interview_prep: (
        InterviewPreparationReport
        | Mapping[str, Any]
        | None
    ),
) -> None:
    if interview_prep is None:
        st.info(
            "Interview preparation has not been generated yet."
        )
        return

    try:
        report = _as_report(
            interview_prep
        )

    except Exception:
        st.error(
            "Saved interview preparation is invalid."
        )
        return

    st.subheader("Interview preparation")

    st.caption(
        f"{report.prep_status} · "
        f"{len(report.questions)} questions"
    )

    st.markdown("### Positioning")
    st.write(
        report.positioning_guidance.summary
    )

    st.markdown("**Focus points**")
    for point in report.positioning_guidance.focus_points:
        st.write(f"- {point}")

    if report.positioning_guidance.avoid_overstating:
        st.markdown("**Avoid overstating**")
        for item in report.positioning_guidance.avoid_overstating:
            st.write(f"- {item}")

    st.markdown("### Questions")
    for question in report.questions:
        with st.expander(
            question.question
        ):
            st.caption(
                f"{question.category} · risk: {question.risk_level}"
            )

            st.write(
                question.why_this_matters
            )

            st.markdown("**Evidence to use**")
            for evidence in question.evidence_to_use:
                st.write(f"- {evidence}")

            st.markdown("**Answer directions**")
            for direction in question.suggested_answer_directions:
                st.write(f"- **{direction.angle}**")
                for point in direction.key_points:
                    st.write(f"  - {point}")
                st.caption(direction.example_focus)

            st.markdown("**Preparation note**")
            st.write(
                question.preparation_note
            )

    st.markdown("### Experience checkpoints")
    for checkpoint in report.experience_checkpoints:
        st.markdown(
            f"**{checkpoint.emphasized_area}**"
        )
        st.write(
            checkpoint.supporting_cv_evidence
        )
        st.caption(
            checkpoint.preparation_needed
        )

    if report.company_specific_talking_points:
        st.markdown("### Company-specific talking points")
        for point in report.company_specific_talking_points:
            st.write(
                f"- **{point.topic}** — {point.how_to_use}"
            )

    st.markdown("### Questions to ask")
    for question in report.candidate_questions_to_ask:
        st.write(
            f"- {question.question}"
        )

    if report.limitations:
        st.markdown("### Limitations")
        for limitation in report.limitations:
            st.write(f"- {limitation}")
