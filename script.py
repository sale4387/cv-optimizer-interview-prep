from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import (
    datetime,
    timezone,
)
from typing import Callable
from unittest.mock import patch

from google.api_core.exceptions import (
    ServiceUnavailable,
)

import services.revision_service as service
from ai.response_models import (
    CVOptimizationResponse,
)
from ai.revision_models import (
    CVRevisionRequest,
)
from ai.workflows.cv_revision import (
    CVRevisionWorkflowError,
    revise_cv_sections,
)
from services.application_service import (
    SavedApplicationResult,
)


BASE_CV = {
    "profile_id": "sale",
    "cv_version": "1.0",
    "personal_info": {
        "full_name": (
            "Aleksandar Markovic"
        ),
        "location": (
            "Gouda, Netherlands"
        ),
        "phone": (
            "+31 00 000 0000"
        ),
        "email": (
            "test@example.com"
        ),
        "linkedin": (
            "https://linkedin.com/in/test"
        ),
    },
    "professional_summary": (
        "Commercial professional with "
        "experience in stakeholder "
        "management and process improvement."
    ),
    "core_skills": [
        "Procurement",
        "Stakeholder management",
        "Python",
    ],
    "professional_experience": [
        {
            "experience_id": (
                "experience_001"
            ),
            "employer": (
                "Example Company"
            ),
            "job_title": (
                "Commercial Manager"
            ),
            "location": (
                "Netherlands"
            ),
            "start_date": "2020",
            "end_date": "Present",
            "responsibilities": [
                (
                    "Managed commercial "
                    "stakeholders and internal "
                    "delivery teams."
                )
            ],
            "achievements": [],
        }
    ],
    "projects": [],
    "education": [
        {
            "education_id": (
                "education_001"
            ),
            "institution": (
                "Example University"
            ),
            "qualification": (
                "Business Degree"
            ),
            "start_date": "2010",
            "end_date": "2014",
        }
    ],
    "languages": [
        {
            "language": "English",
            "level": "Fluent",
        }
    ],
    "tools_and_technologies": [
        "Python",
    ],
}


CURRENT_OPTIMIZATION = {
    "fit_assessment": {
        "level": "strong",
        "explanation": (
            "The candidate has directly "
            "relevant commercial and "
            "stakeholder-management experience "
            "for the target role."
        ),
        "relevant_experience": [
            (
                "Managed commercial "
                "stakeholders and internal "
                "delivery teams."
            )
        ],
        "missing_requirements": [],
    },
    "cv_patch": {
        "professional_summary": (
            "Commercial professional with "
            "experience in stakeholder "
            "management, procurement and "
            "structured process improvement "
            "across operational teams."
        ),
        "experience_updates": [
            {
                "experience_id": (
                    "experience_001"
                ),
                "suggested_job_title": (
                    "Commercial Manager"
                ),
                "responsibilities": [
                    (
                        "Managed commercial "
                        "stakeholders and internal "
                        "delivery teams to improve "
                        "coordination and delivery."
                    )
                ],
            }
        ],
        "skills_to_highlight": [
            "Stakeholder management",
            "Procurement",
        ],
    },
    "gap_analysis": {
        "supported_requirements": [
            (
                "Stakeholder management "
                "experience"
            )
        ],
        "reasonably_derived_requirements": [
            (
                "Cross-functional "
                "coordination"
            )
        ],
        "unsupported_requirements": [],
    },
    "warnings": [],
}


REVISED_SUMMARY = (
    "Commercial and AI project "
    "professional with experience in "
    "stakeholder management, procurement, "
    "Python-enabled workflows and practical "
    "process improvement across teams."
)


def optimization_model(
    data: dict | None = None,
) -> CVOptimizationResponse:
    return (
        CVOptimizationResponse
        .model_validate(
            data
            or CURRENT_OPTIMIZATION
        )
    )


def application_record(
    *,
    status: str = "draft",
    summary: str | None = None,
) -> SavedApplicationResult:
    tailored_cv = deepcopy(
        BASE_CV
    )

    tailored_cv[
        "professional_summary"
    ] = (
        summary
        or CURRENT_OPTIMIZATION[
            "cv_patch"
        ][
            "professional_summary"
        ]
    )

    tailored_cv[
        "professional_experience"
    ][0][
        "responsibilities"
    ] = deepcopy(
        CURRENT_OPTIMIZATION[
            "cv_patch"
        ][
            "experience_updates"
        ][0][
            "responsibilities"
        ]
    )

    tailored_cv[
        "core_skills"
    ] = [
        "Stakeholder management",
        "Procurement",
        "Python",
    ]

    now = datetime.now(
        timezone.utc
    )

    return (
        SavedApplicationResult
        .model_validate(
            {
                "application_id": (
                    "application-001"
                ),
                "profile_id": "sale",
                "company_key": (
                    "example-company-nl"
                ),
                "job_title": (
                    "Commercial AI Manager"
                ),
                "job_ad_hash": "a" * 64,
                "status": status,
                "fit_assessment": (
                    CURRENT_OPTIMIZATION[
                        "fit_assessment"
                    ]
                ),
                "tailored_cv": (
                    tailored_cv
                ),
                "gap_analysis": (
                    CURRENT_OPTIMIZATION[
                        "gap_analysis"
                    ]
                ),
                "interview_prep": None,
                "base_cv_version": "1.0",
                "schema_version": "1.0",
                "prompt_version": (
                    "task-007-v1"
                ),
                "model_version": (
                    "test-model"
                ),
                "created_at": now,
                "updated_at": now,
                "accepted_at": (
                    now
                    if status == "accepted"
                    else None
                ),
            }
        )
    )


def test_accept_updates_status() -> None:
    draft = application_record(
        status="draft"
    )

    accepted = application_record(
        status="accepted"
    )

    updates: list[dict] = []

    with (
        patch.object(
            service,
            "load_saved_application",
            side_effect=[
                draft,
                accepted,
            ],
        ),
        patch.object(
            service,
            "update_application",
            side_effect=lambda application_id, payload: updates.append(
                payload
            ),
        ),
    ):
        result = (
            service
            .accept_saved_application(
                "application-001"
            )
        )

    assert result.status == "accepted"
    assert updates == [
        {
            "status": "accepted",
        }
    ]


def test_comments_can_be_added_edited_removed() -> None:
    added = (
        service
        .normalize_revision_comments(
            {
                "professional_summary": (
                    "Make it more concise."
                ),
                "skills_to_highlight": (
                    "Prioritize Python."
                ),
            }
        )
    )

    assert len(added) == 2

    edited_and_removed = (
        service
        .normalize_revision_comments(
            {
                "professional_summary": (
                    "Focus on commercial AI work."
                ),
                "skills_to_highlight": (
                    "   "
                ),
            }
        )
    )

    assert edited_and_removed == {
        "professional_summary": (
            "Focus on commercial AI work."
        )
    }


def test_revision_updates_selected_section_only() -> None:
    draft = application_record(
        status="draft"
    )

    revised = application_record(
        status="draft",
        summary=REVISED_SUMMARY,
    )

    revised_optimization_data = (
        deepcopy(
            CURRENT_OPTIMIZATION
        )
    )

    revised_optimization_data[
        "cv_patch"
    ][
        "professional_summary"
    ] = REVISED_SUMMARY

    revised_optimization = (
        optimization_model(
            revised_optimization_data
        )
    )

    update_payloads: list[
        dict
    ] = []

    with (
        patch.object(
            service,
            "load_saved_application",
            side_effect=[
                draft,
                revised,
            ],
        ),
        patch.object(
            service,
            "load_cv_profile",
            return_value=(
                deepcopy(BASE_CV)
            ),
        ),
        patch.object(
            service,
            "_build_existing_optimization",
            return_value=(
                optimization_model()
            ),
        ),
        patch.object(
            service,
            "revise_cv_sections",
            return_value=(
                revised_optimization
            ),
        ),
        patch.object(
            service,
            "update_application",
            side_effect=lambda application_id, payload: update_payloads.append(
                payload
            ),
        ),
    ):
        result = (
            service
            .revise_saved_application(
                application_id=(
                    "application-001"
                ),
                comments={
                    "professional_summary": (
                        "Focus on AI delivery."
                    )
                },
            )
        )

    assert result.status == "draft"
    assert (
        result
        .tailored_cv
        .professional_summary
        == REVISED_SUMMARY
    )

    payload = update_payloads[0]

    assert payload["status"] == "draft"

    assert (
        payload["tailored_cv"][
            "professional_experience"
        ][0][
            "responsibilities"
        ]
        == CURRENT_OPTIMIZATION[
            "cv_patch"
        ][
            "experience_updates"
        ][0][
            "responsibilities"
        ]
    )


def test_unrequested_section_is_rejected() -> None:
    request = CVRevisionRequest(
        application_id=(
            "application-001"
        ),
        sections=[
            {
                "section": (
                    "professional_summary"
                ),
                "comment": (
                    "Make it more concise."
                ),
            }
        ],
    )

    response = {
        "professional_summary": (
            REVISED_SUMMARY
        ),
        "skills_to_highlight": [
            "Python"
        ],
    }

    def fake_request(
        prompt: str,
        *,
        system_instruction: str,
    ) -> str:
        return json.dumps(response)

    try:
        revise_cv_sections(
            original_cv=BASE_CV,
            current_cv=BASE_CV,
            current_optimization=(
                optimization_model()
            ),
            revision_request=request,
            request_function=(
                fake_request
            ),
        )

    except CVRevisionWorkflowError:
        return

    raise AssertionError(
        "Unrequested revision section "
        "was accepted."
    )


def test_invalid_revision_is_rejected() -> None:
    request = CVRevisionRequest(
        application_id=(
            "application-001"
        ),
        sections=[
            {
                "section": (
                    "professional_summary"
                ),
                "comment": (
                    "Make it more concise."
                ),
            }
        ],
    )

    def fake_request(
        prompt: str,
        *,
        system_instruction: str,
    ) -> str:
        return json.dumps(
            {
                "professional_summary": (
                    "Too short"
                )
            }
        )

    try:
        revise_cv_sections(
            original_cv=BASE_CV,
            current_cv=BASE_CV,
            current_optimization=(
                optimization_model()
            ),
            revision_request=request,
            request_function=(
                fake_request
            ),
        )

    except CVRevisionWorkflowError:
        return

    raise AssertionError(
        "Invalid revision response "
        "was accepted."
    )


def test_firestore_save_failure_is_controlled() -> None:
    draft = application_record(
        status="draft"
    )

    with (
        patch.object(
            service,
            "load_saved_application",
            return_value=draft,
        ),
        patch.object(
            service,
            "load_cv_profile",
            return_value=(
                deepcopy(BASE_CV)
            ),
        ),
        patch.object(
            service,
            "_build_existing_optimization",
            return_value=(
                optimization_model()
            ),
        ),
        patch.object(
            service,
            "revise_cv_sections",
            return_value=(
                optimization_model()
            ),
        ),
        patch.object(
            service,
            "update_application",
            side_effect=(
                ServiceUnavailable(
                    "Forced Firestore failure"
                )
            ),
        ),
    ):
        try:
            (
                service
                .revise_saved_application(
                    application_id=(
                        "application-001"
                    ),
                    comments={
                        "professional_summary": (
                            "Improve the summary."
                        )
                    },
                )
            )

        except (
            service
            .ApplicationRevisionError
        ):
            return

    raise AssertionError(
        "Firestore revision save "
        "failure was not controlled."
    )


def test_draft_pdf_export_is_blocked() -> None:
    draft = application_record(
        status="draft"
    )

    try:
        (
            service
            .generate_accepted_application_pdf(
                draft
            )
        )

    except service.DraftPDFExportError:
        return

    raise AssertionError(
        "Draft PDF export was not blocked."
    )


def test_accepted_pdf_export_is_allowed() -> None:
    accepted = application_record(
        status="accepted"
    )

    with patch.object(
        service,
        "generate_cv_pdf",
        return_value=b"%PDF-test",
    ):
        result = (
            service
            .generate_accepted_application_pdf(
                accepted
            )
        )

    assert result == b"%PDF-test"


TESTS: list[
    tuple[str, Callable[[], None]]
] = [
    (
        "Accept CV updates status",
        test_accept_updates_status,
    ),
    (
        "Revision comments can be "
        "added, edited and removed",
        test_comments_can_be_added_edited_removed,
    ),
    (
        "Revision updates selected "
        "section and remains draft",
        test_revision_updates_selected_section_only,
    ),
    (
        "Unrequested AI section rejected",
        test_unrequested_section_is_rejected,
    ),
    (
        "Invalid revision response rejected",
        test_invalid_revision_is_rejected,
    ),
    (
        "Firestore revision save "
        "failure controlled",
        test_firestore_save_failure_is_controlled,
    ),
    (
        "Draft PDF export blocked",
        test_draft_pdf_export_is_blocked,
    ),
    (
        "Accepted PDF export allowed",
        test_accepted_pdf_export_is_allowed,
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
                f"{type(error).__name__}: "
                f"{error}"
            )

        else:
            passed += 1

            print(
                f"[PASS] {test_name}"
            )

    print()
    print(
        f"Result: {passed} passed, "
        f"{failed} failed"
    )

    return (
        0
        if failed == 0
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
