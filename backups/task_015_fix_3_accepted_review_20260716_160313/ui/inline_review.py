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


def render_inline_review(application) -> None:
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

    if not state.items:
        st.info(
            "No inline differences were found between the original CV and the tailored CV."
        )
        return

    st.subheader("Inline CV review")

    st.caption(
        "Review each AI-suggested change. Accept the suggestion, keep the original text, or mark the item for targeted revision."
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

    for item in state.items:
        with st.expander(
            f"{item.item_type}: {item.source_reference}"
        ):
            st.markdown("**Original**")
            st.write(item.original_value)

            st.markdown("**AI suggestion**")
            st.write(item.suggested_value)

            decision = st.radio(
                "Decision",
                options=[
                    "pending",
                    "accepted_suggestion",
                    "kept_original",
                    "revision_requested",
                ],
                index=[
                    "pending",
                    "accepted_suggestion",
                    "kept_original",
                    "revision_requested",
                ].index(item.decision)
                if item.decision
                in [
                    "pending",
                    "accepted_suggestion",
                    "kept_original",
                    "revision_requested",
                ]
                else 0,
                key=(
                    "inline_review_decision_"
                    f"{state.application_id}_"
                    f"{item.item_id}"
                ),
            )

            comment = item.user_comment or ""

            if decision == "revision_requested":
                comment = st.text_area(
                    "Targeted revision comment",
                    value=comment,
                    key=(
                        "inline_review_comment_"
                        f"{state.application_id}_"
                        f"{item.item_id}"
                    ),
                )

            if st.button(
                "Save decision",
                key=(
                    "inline_review_save_"
                    f"{state.application_id}_"
                    f"{item.item_id}"
                ),
            ):
                updated_state = update_review_item_decision(
                    state,
                    item_id=item.item_id,
                    decision=decision,
                    user_comment=comment
                    if comment
                    else None,
                )

                _save_state(
                    application,
                    updated_state,
                )

                st.rerun()
