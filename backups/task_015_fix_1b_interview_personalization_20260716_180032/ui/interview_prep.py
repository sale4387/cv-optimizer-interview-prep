from __future__ import annotations

from typing import Any

import streamlit as st

from services.interview_prep_service import ensure_application_interview_prep


def _to_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            pass
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass
    return {}


def render_application_interview_prep(application: Any) -> None:
    app = _to_dict(application)
    prep = ensure_application_interview_prep(app)

    st.subheader("Interview preparation")
    st.caption("Application-specific prep based on the selected role, job ad, tailored CV and fit/gap context.")

    if prep.get("status") != "complete":
        st.warning(prep.get("reason") or "Interview preparation is not available for this application.")
        warnings = prep.get("prep_warnings") or []
        for warning in warnings:
            st.write(f"- {warning}")
        return

    questions = prep.get("likely_interviewer_questions") or []
    candidate_questions = prep.get("candidate_questions_to_ask") or []
    warnings = prep.get("prep_warnings") or []

    st.markdown(f"**Likely interviewer questions:** {len(questions)}")

    if warnings:
        with st.expander("Prep warnings", expanded=True):
            for warning in warnings:
                st.write(f"- {warning}")

    st.markdown("#### Likely questions from the interviewer")

    for index, item in enumerate(questions, start=1):
        question = item.get("question", "").strip()
        title = question if question else f"Question {index}"

        with st.expander(f"{index}. {title}", expanded=False):
            why = item.get("why_it_may_be_asked")
            answer_angle = item.get("answer_angle")
            evidence = item.get("evidence_to_use")
            risk = item.get("risk_level")

            if why:
                st.markdown(f"**Why this may be asked:** {why}")
            if answer_angle:
                st.markdown(f"**Answer angle:** {answer_angle}")
            if evidence:
                st.markdown(f"**Evidence to use:** {evidence}")
            if risk:
                st.markdown(f"**Risk level:** {risk}")

    st.markdown("#### Candidate questions to ask")
    for question in candidate_questions:
        st.write(f"- {question}")

    source_notes = prep.get("source_notes") or []
    if source_notes:
        with st.expander("Source notes", expanded=False):
            for note in source_notes:
                st.write(f"- {note}")
