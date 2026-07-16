from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from services.interview_prep_service import (
    ensure_application_interview_prep,
)


def _to_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)

    if hasattr(value, "model_dump"):
        try:
            return value.model_dump(
                mode="python"
            )
        except TypeError:
            return value.model_dump()
        except Exception:
            pass

    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass

    return {}


def _render_legacy_prep(
    prep: Mapping[str, Any],
) -> None:
    st.caption(
        "Legacy interview preparation. Create a new "
        "application to generate the personalized format."
    )

    questions = prep.get(
        "likely_interviewer_questions"
    ) or []

    st.markdown(
        f"**Likely interviewer questions:** "
        f"{len(questions)}"
    )

    for index, item in enumerate(
        questions,
        start=1,
    ):
        if not isinstance(
            item,
            Mapping,
        ):
            continue

        question = str(
            item.get("question")
            or f"Question {index}"
        )

        with st.expander(
            f"{index}. {question}",
            expanded=False,
        ):
            for label, key in (
                (
                    "Why this may be asked",
                    "why_it_may_be_asked",
                ),
                (
                    "Answer angle",
                    "answer_angle",
                ),
                (
                    "Evidence to use",
                    "evidence_to_use",
                ),
                (
                    "Risk level",
                    "risk_level",
                ),
            ):
                value = item.get(key)

                if value:
                    st.markdown(
                        f"**{label}:** {value}"
                    )

    st.markdown(
        "#### Candidate questions to ask"
    )

    for question in (
        prep.get(
            "candidate_questions_to_ask"
        )
        or []
    ):
        st.write(f"- {question}")


def _render_positioning(
    positioning: Mapping[str, Any],
) -> None:
    st.markdown(
        "#### Positioning for this role"
    )
    st.write(
        positioning.get("summary")
        or ""
    )

    focus_points = positioning.get(
        "focus_points"
    ) or []

    if focus_points:
        st.markdown(
            "**What to emphasize**"
        )

        for point in focus_points:
            st.write(f"- {point}")

    avoid = positioning.get(
        "avoid_overstating"
    ) or []

    if avoid:
        st.markdown(
            "**Avoid overstating**"
        )

        for point in avoid:
            st.warning(str(point))


def _render_question(
    item: Mapping[str, Any],
    index: int,
) -> None:
    question = str(
        item.get("question")
        or f"Question {index}"
    ).strip()

    risk = str(
        item.get("risk_level")
        or "medium"
    ).upper()

    category = str(
        item.get("category")
        or ""
    ).replace(
        "_",
        " ",
    ).title()

    with st.expander(
        f"{index}. {question}",
        expanded=False,
    ):
        st.caption(
            f"{category} · {risk} risk"
        )

        why = item.get(
            "why_this_matters"
        )

        if why:
            st.markdown(
                "**Why this is likely**"
            )
            st.write(why)

        evidence = item.get(
            "evidence_to_use"
        ) or []

        if evidence:
            st.markdown(
                "**Evidence from your CV/context**"
            )

            for evidence_item in evidence:
                st.write(
                    f"- {evidence_item}"
                )

        directions = item.get(
            "suggested_answer_directions"
        ) or []

        if directions:
            st.markdown(
                "**Suggested answers**"
            )

            for direction_index, direction in enumerate(
                directions,
                start=1,
            ):
                if not isinstance(
                    direction,
                    Mapping,
                ):
                    continue

                st.markdown(
                    f"**Option {direction_index}: "
                    f"{direction.get('angle', '')}**"
                )

                for point in (
                    direction.get(
                        "key_points"
                    )
                    or []
                ):
                    st.write(
                        f"- {point}"
                    )

                draft = direction.get(
                    "example_focus"
                )

                if draft:
                    st.markdown(
                        "**Suggested answer draft**"
                    )
                    st.write(draft)

        note = item.get(
            "preparation_note"
        )

        if note:
            st.markdown(
                "**Preparation note**"
            )
            st.write(note)


def _render_canonical_prep(
    prep: Mapping[str, Any],
) -> None:
    positioning = prep.get(
        "positioning_guidance"
    )

    if isinstance(
        positioning,
        Mapping,
    ):
        _render_positioning(
            positioning
        )

    questions = prep.get(
        "questions"
    ) or []

    st.markdown(
        f"#### Likely interviewer questions "
        f"({len(questions)})"
    )

    for index, item in enumerate(
        questions,
        start=1,
    ):
        if isinstance(
            item,
            Mapping,
        ):
            _render_question(
                item,
                index,
            )

    checkpoints = prep.get(
        "experience_checkpoints"
    ) or []

    if checkpoints:
        with st.expander(
            "Experience to refresh",
            expanded=False,
        ):
            for checkpoint in checkpoints:
                if not isinstance(
                    checkpoint,
                    Mapping,
                ):
                    continue

                st.markdown(
                    f"**{checkpoint.get('emphasized_area', '')}**"
                )
                st.write(
                    checkpoint.get(
                        "supporting_cv_evidence"
                    )
                    or ""
                )
                st.caption(
                    checkpoint.get(
                        "preparation_needed"
                    )
                    or ""
                )

    talking_points = prep.get(
        "company_specific_talking_points"
    ) or []

    if talking_points:
        with st.expander(
            "Company-specific talking points",
            expanded=False,
        ):
            for point in talking_points:
                if not isinstance(
                    point,
                    Mapping,
                ):
                    continue

                st.markdown(
                    f"**{point.get('topic', '')}**"
                )
                st.write(
                    point.get(
                        "how_to_use"
                    )
                    or ""
                )

    st.markdown(
        "#### Candidate questions to ask"
    )

    for item in (
        prep.get(
            "candidate_questions_to_ask"
        )
        or []
    ):
        if isinstance(item, Mapping):
            st.markdown(
                f"- **{item.get('question', '')}**"
            )

            reason = item.get(
                "reason"
            )

            if reason:
                st.caption(reason)

        else:
            st.write(f"- {item}")

    limitations = prep.get(
        "limitations"
    ) or []

    for limitation in limitations:
        st.warning(str(limitation))


def render_application_interview_prep(
    application: Any,
) -> None:
    app = _to_dict(application)
    prep = ensure_application_interview_prep(
        app
    )

    st.subheader(
        "Interview preparation"
    )
    st.caption(
        "Generated for this application from the "
        "job ad, company context, fit/gap and CV."
    )

    if (
        prep.get("prep_status")
        == "limited"
        and not prep.get("questions")
    ):
        st.warning(
            prep.get("reason")
            or "Interview preparation is unavailable."
        )
        return

    if isinstance(
        prep.get("questions"),
        list,
    ):
        _render_canonical_prep(
            prep
        )
        return

    _render_legacy_prep(
        prep
    )
