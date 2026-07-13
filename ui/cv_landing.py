from __future__ import annotations

import streamlit as st

from services.candidate_profile_service import (
    CandidateProfileError,
    get_default_candidate_profile,
    list_candidate_options,
    load_candidate_cv,
)
from ui.cv_preview import render_cv_preview


def _query_value(name: str) -> str | None:
    value = st.query_params.get(name)

    if isinstance(value, list):
        return value[0] if value else None

    return value


def _profile_index(options, profile_id: str) -> int:
    for index, option in enumerate(options):
        if option.profile_id == profile_id:
            return index

    return 0


def _set_query_params(*, page: str, profile_id: str) -> None:
    st.query_params.from_dict(
        {
            "page": page,
            "profile": profile_id,
        }
    )


def render_cv_landing_page() -> None:
    try:
        options = list_candidate_options()
        default_profile = get_default_candidate_profile()

    except CandidateProfileError as error:
        st.error(str(error))
        return

    requested_profile_id = (
        _query_value("profile")
        or default_profile.profile_id
    )

    selected_index = _profile_index(
        options,
        requested_profile_id,
    )

    selected_profile = st.selectbox(
        "Candidate profile",
        options=options,
        index=selected_index,
        format_func=lambda option: option.display_name,
        key="cv_first_profile_selector",
    )

    if selected_profile.profile_id != requested_profile_id:
        _set_query_params(
            page="cv",
            profile_id=selected_profile.profile_id,
        )
        st.rerun()

    st.title("Stored CV")

    st.caption(
        f"{selected_profile.display_name} · "
        f"profile={selected_profile.profile_id}"
    )

    if st.button(
        "Optimize this CV",
        width="stretch",
    ):
        _set_query_params(
            page="optimize",
            profile_id=selected_profile.profile_id,
        )
        st.rerun()

    try:
        cv = load_candidate_cv(
            selected_profile.profile_id
        )

    except CandidateProfileError as error:
        st.error(str(error))
        return

    render_cv_preview(cv)
