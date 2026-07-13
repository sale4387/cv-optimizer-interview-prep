from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

from cv_data.models import CVProfile
from services.inline_review_service import (
    InlineReviewError,
    build_inline_review_state,
    review_state_ready_to_accept,
    update_review_item_decision,
)


def load_base_cv() -> CVProfile:
    return CVProfile.model_validate_json(
        Path("cv_data/cv_sale.json").read_text(
            encoding="utf-8"
        )
    )


def make_application(
    *,
    tailored_cv: dict | None,
):
    return SimpleNamespace(
        application_id="app-019-test",
        profile_id="sale",
        tailored_cv=tailored_cv,
    )


def make_tailored_cv() -> dict:
    base = load_base_cv().model_dump(
        mode="python"
    )

    tailored = deepcopy(base)

    tailored["professional_summary"] = (
        tailored["professional_summary"]
        + " Tailored for this specific job application."
    )

    if tailored.get("core_skills"):
        tailored["core_skills"] = (
            list(tailored["core_skills"])
            + ["Job-specific stakeholder alignment"]
        )

    if tailored.get("tools_and_technologies"):
        tailored["tools_and_technologies"] = (
            list(tailored["tools_and_technologies"])
            + ["Applicant tracking systems"]
        )

    experiences = tailored.get(
        "professional_experience",
        [],
    )

    if experiences:
        responsibilities = experiences[0].setdefault(
            "responsibilities",
            [],
        )

        responsibilities.append(
            "Tailored responsibility for the tested job application."
        )

    return tailored


def test_inline_review_state_created() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    assert state.application_id == "app-019-test"
    assert state.items


def test_summary_review_item_exists() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    item_types = {
        item.item_type
        for item in state.items
    }

    assert "professional_summary" in item_types


def test_core_skills_or_tools_review_item_exists() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    item_types = {
        item.item_type
        for item in state.items
    }

    assert (
        "core_skills" in item_types
        or "tools_and_technologies" in item_types
    )


def test_responsibility_review_item_exists() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    item_types = {
        item.item_type
        for item in state.items
    }

    assert "responsibility_bullet" in item_types


def test_missing_tailored_cv_rejected() -> None:
    application = make_application(
        tailored_cv=None
    )

    try:
        build_inline_review_state(
            application
        )

    except InlineReviewError:
        return

    raise AssertionError(
        "Application without tailored CV was accepted for inline review."
    )


def test_accept_suggestion_decision_updates_item() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    first_item = state.items[0]

    updated = update_review_item_decision(
        state,
        item_id=first_item.item_id,
        decision="accepted_suggestion",
    )

    updated_item = updated.items[0]

    assert updated_item.decision == "accepted_suggestion"
    assert updated_item.current_value == updated_item.suggested_value


def test_keep_original_decision_updates_item() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    first_item = state.items[0]

    updated = update_review_item_decision(
        state,
        item_id=first_item.item_id,
        decision="kept_original",
    )

    updated_item = updated.items[0]

    assert updated_item.decision == "kept_original"
    assert updated_item.current_value == updated_item.original_value


def test_revision_request_sets_pending_status() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    first_item = state.items[0]

    updated = update_review_item_decision(
        state,
        item_id=first_item.item_id,
        decision="revision_requested",
        user_comment="Make this more precise.",
    )

    updated_item = updated.items[0]

    assert updated_item.decision == "revision_requested"
    assert updated_item.revision_status == "pending"
    assert updated_item.user_comment == "Make this more precise."


def test_ready_to_accept_false_with_pending_items() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    assert review_state_ready_to_accept(
        state
    ) is False


def test_ready_to_accept_true_when_all_resolved() -> None:
    application = make_application(
        tailored_cv=make_tailored_cv()
    )

    state = build_inline_review_state(
        application
    )

    for item in state.items:
        state = update_review_item_decision(
            state,
            item_id=item.item_id,
            decision="accepted_suggestion",
        )

    assert review_state_ready_to_accept(
        state
    ) is True


def test_streamlit_app_patched() -> None:
    app_text = Path("streamlit/app.py").read_text(
        encoding="utf-8"
    )

    assert "render_inline_review" in app_text
    assert "Request changes is available only" in app_text


def test_inline_review_ui_imports() -> None:
    from ui.inline_review import render_inline_review

    assert callable(render_inline_review)


TESTS: list[
    tuple[str, Callable[[], None]]
] = [
    (
        "Inline review state created",
        test_inline_review_state_created,
    ),
    (
        "Summary review item exists",
        test_summary_review_item_exists,
    ),
    (
        "Core skills or tools review item exists",
        test_core_skills_or_tools_review_item_exists,
    ),
    (
        "Responsibility review item exists",
        test_responsibility_review_item_exists,
    ),
    (
        "Missing tailored CV rejected",
        test_missing_tailored_cv_rejected,
    ),
    (
        "Accept suggestion decision updates item",
        test_accept_suggestion_decision_updates_item,
    ),
    (
        "Keep original decision updates item",
        test_keep_original_decision_updates_item,
    ),
    (
        "Revision request sets pending status",
        test_revision_request_sets_pending_status,
    ),
    (
        "Ready to accept false with pending items",
        test_ready_to_accept_false_with_pending_items,
    ),
    (
        "Ready to accept true when all resolved",
        test_ready_to_accept_true_when_all_resolved,
    ),
    (
        "Streamlit app patched",
        test_streamlit_app_patched,
    ),
    (
        "Inline review UI imports",
        test_inline_review_ui_imports,
    ),
]


def main() -> int:
    passed = 0
    failed = 0

    for (
        test_name,
        test_function,
    ) in TESTS:
        try:
            test_function()

        except Exception as error:
            failed += 1

            print(
                f"[FAIL] {test_name} — "
                f"{type(error).__name__}: {error}"
            )

        else:
            passed += 1
            print(f"[PASS] {test_name}")

    print()
    print(
        f"Result: {passed} passed, {failed} failed"
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
