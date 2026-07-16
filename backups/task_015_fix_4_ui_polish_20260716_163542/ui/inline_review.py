from __future__ import annotations

import streamlit as st

from services.inline_review_service import (
    InlineReviewError,
    ReviewState,
    build_inline_review_state,
    review_state_ready_to_accept,
    update_review_item_decision,
)


def _review_state_key(application) -> str:
    return (
        "inline_review_state_"
        f"{application.application_id}"
    )


def _load_state(application) -> ReviewState:
    key = _review_state_key(application)

    if key not in st.session_state:
        st.session_state[key] = (
            build_inline_review_state(
                application
            )
        )

    value = st.session_state[key]

    if isinstance(value, ReviewState):
        return value

    return ReviewState.model_validate(value)


def _save_state(
    application,
    state: ReviewState,
) -> None:
    st.session_state[
        _review_state_key(application)
    ] = state


def _review_feedback_key(
    application,
) -> str:
    return (
        "inline_review_feedback_"
        f"{application.application_id}"
    )


def _decision_widget_key(
    state: ReviewState,
    item_id: str,
) -> str:
    return (
        "inline_review_decision_"
        f"{state.application_id}_"
        f"{item_id}"
    )


def _comment_widget_key(
    state: ReviewState,
    item_id: str,
) -> str:
    return (
        "inline_review_comment_"
        f"{state.application_id}_"
        f"{item_id}"
    )


def render_inline_review(application) -> None:
    if getattr(
        application,
        "status",
        None,
    ) == "accepted":
        return

    if application.tailored_cv is None:
        st.info(
            "Inline review is available only when a tailored CV exists."
        )
        return

    try:
        state = _load_state(application)

    except InlineReviewError as error:
        st.warning(str(error))
        return

    feedback_key = _review_feedback_key(
        application
    )

    if st.session_state.pop(
        feedback_key,
        False,
    ):
        st.success(
            "Review decisions saved."
        )

    if not state.items:
        st.info(
            "No inline differences were found between the original CV and the tailored CV."
        )
        return

    st.subheader("Inline CV review")

    st.caption(
        "Review the suggestions, then save all decisions together."
    )

    ready = review_state_ready_to_accept(
        state
    )

    if ready:
        st.success(
            "All inline review items are resolved."
        )
    else:
        st.warning(
            "Some inline review items are still pending."
        )

    available_decisions = [
        "pending",
        "accepted_suggestion",
        "kept_original",
        "revision_requested",
    ]

    for item in state.items:
        with st.expander(
            f"{item.item_type}: {item.source_reference}"
        ):
            st.markdown("**Original**")
            st.write(item.original_value)

            st.markdown("**AI suggestion**")
            st.write(item.suggested_value)

            decision_key = _decision_widget_key(
                state,
                item.item_id,
            )

            decision = st.radio(
                "Decision",
                options=available_decisions,
                index=(
                    available_decisions.index(
                        item.decision
                    )
                    if item.decision
                    in available_decisions
                    else 0
                ),
                key=decision_key,
            )

            if decision == "revision_requested":
                st.text_area(
                    "Targeted revision comment",
                    value=item.user_comment or "",
                    key=_comment_widget_key(
                        state,
                        item.item_id,
                    ),
                )

    if st.button(
        "Save all decisions",
        key=(
            "inline_review_save_all_"
            f"{state.application_id}"
        ),
        type="primary",
        width="stretch",
    ):
        updated_state = state

        for item in state.items:
            decision = st.session_state.get(
                _decision_widget_key(
                    state,
                    item.item_id,
                ),
                item.decision,
            )

            comment = None

            if decision == "revision_requested":
                raw_comment = st.session_state.get(
                    _comment_widget_key(
                        state,
                        item.item_id,
                    ),
                    item.user_comment or "",
                )

                comment = (
                    str(raw_comment).strip()
                    or None
                )

            updated_state = (
                update_review_item_decision(
                    updated_state,
                    item_id=item.item_id,
                    decision=decision,
                    user_comment=comment,
                )
            )

        _save_state(
            application,
            updated_state,
        )

        st.session_state[
            feedback_key
        ] = True

        st.rerun()

