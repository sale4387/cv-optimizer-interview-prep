#!/usr/bin/env python3
from __future__ import annotations

import copy
import logging
import py_compile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


PROJECT_ROOT = Path.cwd()

logging.disable(
    logging.CRITICAL
)


def _cv_data() -> dict:
    return {
        "profile_id": "sale",
        "cv_version": "1.0",
        "personal_info": {
            "full_name": "Test Candidate",
            "location": "Netherlands",
            "phone": "+31000000000",
            "email": "test@example.com",
            "linkedin": (
                "https://linkedin.com/in/test"
            ),
        },
        "professional_summary": (
            "Commercial and product-oriented professional "
            "with extensive account management, partnership "
            "and technical workflow experience."
        ),
        "core_skills": [
            "Project Management",
            "Product Ownership",
            "Partnership Management",
            "Account Management",
        ],
        "professional_experience": [
            {
                "experience_id": "exp_001",
                "employer": "Example Company",
                "job_title": "Account Manager",
                "location": "Netherlands",
                "start_date": "2020",
                "end_date": "Present",
                "responsibilities": [
                    "Original responsibility one.",
                    "Original responsibility two.",
                ],
                "achievements": [
                    "Original achievement."
                ],
            }
        ],
        "projects": [],
        "education": [
            {
                "education_id": "edu_001",
                "institution": "University",
                "qualification": "Bachelor Degree",
                "start_date": "2006",
                "end_date": "2010",
            }
        ],
        "languages": [
            {
                "language": "English",
                "level": "Advanced",
            }
        ],
        "tools_and_technologies": [
            "Python"
        ],
    }


def _application(
    tailored_cv,
):
    return SimpleNamespace(
        application_id="app-final-quality",
        profile_id="sale",
        status="draft",
        tailored_cv=tailored_cv,
    )


def _test_compile() -> None:
    files = (
        "ai/prompts.py",
        "services/interview_prep_service.py",
        "services/inline_review_service.py",
        "ui/inline_review.py",
        "streamlit/app.py",
    )

    for name in files:
        py_compile.compile(
            str(PROJECT_ROOT / name),
            doraise=True,
        )


def _test_prompt_safety() -> None:
    from ai.prompts import (
        INTERVIEW_PREP_SYSTEM_INSTRUCTION,
        build_interview_prep_prompt,
    )
    from services.interview_prep_service import (
        INTERVIEW_PREP_PROMPT_VERSION,
    )

    instruction = (
        INTERVIEW_PREP_SYSTEM_INSTRUCTION
    ).lower()

    required = (
        "past-tense claims",
        "future or conditional bridge",
        "do not infer",
        "preparation_note",
    )

    for fragment in required:
        if fragment not in instruction:
            raise AssertionError(
                "Missing interview factual-safety rule: "
                f"{fragment}"
            )

    prompt = build_interview_prep_prompt(
        application_id="app-test",
        original_cv={},
        tailored_cv={},
        job_ad="x" * 120,
        company_research=None,
        generated_at="2026-07-16",
    ).lower()

    if (
        "unsupported tactics or gap-closing actions"
        not in prompt
    ):
        raise AssertionError(
            "Prompt does not preserve useful "
            "stretch-fit bridging."
        )

    if (
        INTERVIEW_PREP_PROMPT_VERSION
        != "task-015-final-quality-v1"
    ):
        raise AssertionError(
            "Prompt version was not updated."
        )


def _test_keep_original_and_removal() -> None:
    import services.inline_review_service as service

    from cv_data.models import CVProfile
    from services.inline_review_service import (
        build_inline_review_state,
        save_inline_review_decisions,
        update_review_item_decision,
    )

    original = CVProfile.model_validate(
        _cv_data()
    )

    tailored = copy.deepcopy(
        _cv_data()
    )

    tailored["core_skills"] = [
        "Account Management",
        "Partnership Management",
        "Project Management",
        "Product Ownership",
    ]

    tailored[
        "professional_experience"
    ][0][
        "responsibilities"
    ] = [
        "AI responsibility one.",
    ]

    application = _application(
        tailored
    )

    updates: list[dict] = []

    def capture_update(
        application_id: str,
        application_updates: dict,
    ) -> str:
        updates.append(
            copy.deepcopy(
                application_updates
            )
        )
        return application_id

    with (
        patch.object(
            service,
            "_load_original_cv_for_application",
            return_value=original,
        ),
        patch.object(
            service,
            "update_application",
            side_effect=capture_update,
        ),
    ):
        state = build_inline_review_state(
            application
        )

        state = update_review_item_decision(
            state,
            item_id="core_skills",
            decision="kept_original",
        )

        for item in list(
            state.items
        ):
            if item.item_id == "core_skills":
                continue

            state = update_review_item_decision(
                state,
                item_id=item.item_id,
                decision="accepted_suggestion",
            )

        saved_state = (
            save_inline_review_decisions(
                application,
                state,
            )
        )

    if (
        saved_state.review_status
        != "complete"
    ):
        raise AssertionError(
            "Resolved review was not completed."
        )

    if len(updates) != 1:
        raise AssertionError(
            "Review decisions were not saved once."
        )

    final_cv = updates[0][
        "tailored_cv"
    ]

    if final_cv[
        "core_skills"
    ] != _cv_data()[
        "core_skills"
    ]:
        raise AssertionError(
            "kept_original did not preserve "
            "the exact skill order."
        )

    responsibilities = final_cv[
        "professional_experience"
    ][0][
        "responsibilities"
    ]

    if responsibilities != [
        "AI responsibility one."
    ]:
        raise AssertionError(
            "Accepted empty AI bullet did not "
            "remove the original bullet."
        )


def _test_revision_is_applied() -> None:
    import services.inline_review_service as service
    import services.revision_service as revision_service

    from cv_data.models import CVProfile
    from services.inline_review_service import (
        build_inline_review_state,
        save_inline_review_decisions,
        update_review_item_decision,
    )

    original = CVProfile.model_validate(
        _cv_data()
    )

    tailored = copy.deepcopy(
        _cv_data()
    )

    tailored[
        "professional_summary"
    ] = (
        "Initial AI professional summary with "
        "commercial and technical positioning "
        "for the selected role."
    )

    application = _application(
        tailored
    )

    revised_data = copy.deepcopy(
        tailored
    )

    revised_data[
        "professional_summary"
    ] = (
        "Revised professional summary with concise "
        "commercial and technical positioning for "
        "the selected account management role."
    )

    revised_application = _application(
        CVProfile.model_validate(
            revised_data
        )
    )

    updates: list[dict] = []

    with (
        patch.object(
            service,
            "_load_original_cv_for_application",
            return_value=original,
        ),
        patch.object(
            revision_service,
            "revise_saved_application",
            return_value=revised_application,
        ) as revise_mock,
        patch.object(
            service,
            "update_application",
            side_effect=lambda app_id, data: (
                updates.append(
                    copy.deepcopy(data)
                )
                or app_id
            ),
        ),
    ):
        state = build_inline_review_state(
            application
        )

        state = update_review_item_decision(
            state,
            item_id="professional_summary",
            decision="revision_requested",
            user_comment="Make it shorter.",
        )

        saved_state = (
            save_inline_review_decisions(
                application,
                state,
            )
        )

    revise_mock.assert_called_once()

    summary_item = next(
        item
        for item in saved_state.items
        if item.item_id
        == "professional_summary"
    )

    if (
        summary_item.decision
        != "revised"
    ):
        raise AssertionError(
            "Revision request was not marked revised."
        )

    if updates[0][
        "tailored_cv"
    ][
        "professional_summary"
    ] != revised_data[
        "professional_summary"
    ]:
        raise AssertionError(
            "Revised summary was not persisted."
        )


def _test_accept_is_guarded() -> None:
    source = (
        PROJECT_ROOT
        / "streamlit"
        / "app.py"
    ).read_text(
        encoding="utf-8"
    )

    required = (
        "review_ready: bool",
        "disabled=not review_ready",
        "Save and resolve all inline review",
    )

    for fragment in required:
        if fragment not in source:
            raise AssertionError(
                "Accept guard is missing: "
                f"{fragment}"
            )


def main() -> int:
    try:
        _test_compile()
        _test_prompt_safety()
        _test_keep_original_and_removal()
        _test_revision_is_applied()
        _test_accept_is_guarded()

    except Exception as error:
        print(
            "[FAIL] TASK-015 FINAL-QUALITY: "
            f"{error}"
        )
        return 1

    print(
        "[PASS] TASK-015 FINAL-QUALITY tests passed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
