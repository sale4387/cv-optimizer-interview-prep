from __future__ import annotations

import json
import logging
import sys
from copy import deepcopy
from typing import Callable

from ai.cleaner import CleanerError, clean_ai_json_response
from ai.validation import (
    ResponseValidationError,
    collect_validation_errors,
    validate_cv_optimization_response,
)
from logger import logger


ORIGINAL_CV = {
    "profile_id": "sale",
    "professional_summary": (
        "Commercial and AI project professional with experience in "
        "stakeholder management, procurement, Python and process improvement."
    ),
    "experience": [
        {
            "id": "experience_001",
            "company": "Example Company",
            "job_title": "Commercial Manager",
            "responsibilities": [
                "Led stakeholder management across commercial and operational teams.",
                "Improved procurement and reporting processes using structured analysis.",
            ],
        },
        {
            "id": "experience_002",
            "company": "Second Company",
            "job_title": "Account Manager",
            "responsibilities": [
                "Managed customer relationships and coordinated internal delivery teams.",
            ],
        },
    ],
    "skills": [
        "Stakeholder management",
        "Procurement",
        "Python",
        "Process improvement",
        "Customer relationship management",
    ],
}


VALID_RESPONSE = {
    "fit_assessment": {
        "level": "strong",
        "explanation": (
            "The candidate has directly relevant commercial, stakeholder-management "
            "and process-improvement experience that matches the central requirements."
        ),
        "relevant_experience": [
            "Led stakeholder management across commercial and operational teams.",
        ],
        "missing_requirements": [],
    },
    "cv_patch": {
        "professional_summary": (
            "Commercial and AI project professional with experience in stakeholder "
            "management, procurement, Python-based workflow development and process "
            "improvement across customer-facing and operational environments."
        ),
        "experience_updates": [
            {
                "experience_id": "experience_001",
                "suggested_job_title": None,
                "responsibilities": [
                    "Led stakeholder management across commercial and operational teams "
                    "to improve coordination and delivery.",
                ],
            }
        ],
        "skills_to_highlight": [
            "Stakeholder management",
            "Procurement",
            "Python",
        ],
    },
    "gap_analysis": {
        "supported_requirements": [
            "Stakeholder management experience",
            "Procurement experience",
        ],
        "reasonably_derived_requirements": [
            "Cross-functional process improvement",
        ],
        "unsupported_requirements": [
            {
                "requirement": "Direct experience with a specific enterprise platform",
                "impact": "medium",
                "preparation_recommendation": (
                    "Review the platform fundamentals and prepare comparable examples "
                    "from existing workflow and systems experience."
                ),
                "interview_guidance": (
                    "State clearly that direct platform experience is limited, then "
                    "connect the gap to proven experience learning adjacent systems."
                ),
            }
        ],
    },
    "warnings": [],
}


class LogCaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def assert_log_contains(
    records: list[logging.LogRecord],
    expected_text: str,
) -> None:
    messages = [record.getMessage() for record in records]

    assert any(
        expected_text in message
        for message in messages
    ), f"Expected log containing '{expected_text}' was not found."


def validate_payload(payload: dict) -> None:
    validate_cv_optimization_response(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )


def test_normal_flow() -> None:
    raw_response = json.dumps(VALID_RESPONSE)

    cleaned = clean_ai_json_response(raw_response)
    validated = validate_cv_optimization_response(
        response_data=cleaned,
        original_cv=ORIGINAL_CV,
    )

    assert validated.fit_assessment.level == "strong"
    assert validated.cv_patch is not None


def test_markdown_wrapper() -> None:
    raw_response = (
        "```json\n"
        + json.dumps(VALID_RESPONSE, indent=2)
        + "\n```"
    )

    cleaned = clean_ai_json_response(raw_response)
    validate_payload(cleaned)

    assert cleaned == VALID_RESPONSE


def test_surrounding_text() -> None:
    raw_response = (
        "Here is the requested result:\n\n"
        + json.dumps(VALID_RESPONSE)
        + "\n\nThis completes the analysis."
    )

    cleaned = clean_ai_json_response(raw_response)
    validate_payload(cleaned)

    assert cleaned == VALID_RESPONSE


def test_missing_keys_lists_all_reasons() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload.pop("warnings")
    payload.pop("gap_analysis")

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    combined = " | ".join(reasons)

    assert "warnings" in combined
    assert "gap_analysis" in combined
    assert len(reasons) >= 2


def test_wrong_type() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["fit_assessment"]["relevant_experience"] = "not-a-list"

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    assert any(
        "relevant_experience" in reason
        for reason in reasons
    )


def test_wrong_size() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["fit_assessment"]["explanation"] = "Too short"
    payload["cv_patch"]["experience_updates"] = []
    payload["cv_patch"]["skills_to_highlight"] = []

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    combined = " | ".join(reasons)

    assert "explanation" in combined
    assert "experience_updates" in combined
    assert "skills_to_highlight" in combined


def test_invalid_enum() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["fit_assessment"]["level"] = "excellent"
    payload["gap_analysis"]["unsupported_requirements"][0]["impact"] = "critical"

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    combined = " | ".join(reasons)

    assert "fit_assessment.level" in combined
    assert "impact" in combined


def test_poor_fit_violation() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["fit_assessment"]["level"] = "poor"

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    assert any(
        "cv_patch must be null" in reason
        for reason in reasons
    )


def test_non_poor_fit_requires_patch() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["fit_assessment"]["level"] = "solid"
    payload["cv_patch"] = None

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    assert any(
        "cv_patch is required" in reason
        for reason in reasons
    )


def test_cleaner_failure_is_logged() -> None:
    handler = LogCaptureHandler()
    logger.addHandler(handler)

    try:
        try:
            clean_ai_json_response(
                "This response contains no JSON object."
            )
        except CleanerError:
            pass
        else:
            raise AssertionError(
                "Cleaner accepted a response without valid JSON."
            )
    finally:
        logger.removeHandler(handler)

    assert_log_contains(
        handler.records,
        "AI response cleaner failed",
    )


def test_unexpected_field_rejected() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["unexpected_field"] = "not allowed"

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    assert any(
        "unexpected_field" in reason
        for reason in reasons
    )


def test_invalid_experience_id_rejected() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["cv_patch"]["experience_updates"][0][
        "experience_id"
    ] = "experience_999"

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    assert any(
        "does not exist in the original CV" in reason
        for reason in reasons
    )


def test_unsupported_skill_rejected() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload["cv_patch"]["skills_to_highlight"].append(
        "Quantum computing"
    )

    reasons = collect_validation_errors(
        response_data=payload,
        original_cv=ORIGINAL_CV,
    )

    assert any(
        "Quantum computing" in reason
        and "not supported by the original CV" in reason
        for reason in reasons
    )


def test_all_validation_failures_are_logged() -> None:
    payload = deepcopy(VALID_RESPONSE)
    payload.pop("warnings")
    payload["fit_assessment"]["explanation"] = "Short"

    handler = LogCaptureHandler()
    logger.addHandler(handler)

    try:
        try:
            validate_cv_optimization_response(
                response_data=payload,
                original_cv=ORIGINAL_CV,
            )
        except ResponseValidationError as error:
            assert len(error.reasons) >= 2
        else:
            raise AssertionError(
                "Invalid response did not raise ResponseValidationError."
            )
    finally:
        logger.removeHandler(handler)

    assert_log_contains(
        handler.records,
        "CV response validation failed",
    )


TESTS: list[tuple[str, Callable[[], None]]] = [
    ("Valid response cleaned and validated", test_normal_flow),
    ("Markdown JSON wrapper extracted", test_markdown_wrapper),
    ("Surrounding AI text removed", test_surrounding_text),
    ("Missing keys list all reasons", test_missing_keys_lists_all_reasons),
    ("Wrong field type rejected", test_wrong_type),
    ("Wrong field and list sizes rejected", test_wrong_size),
    ("Unsupported enum values rejected", test_invalid_enum),
    ("Poor fit with CV patch rejected", test_poor_fit_violation),
    ("Non-poor fit without CV patch rejected", test_non_poor_fit_requires_patch),
    ("Cleaner failure rejected and logged", test_cleaner_failure_is_logged),
    ("Unexpected JSON field rejected", test_unexpected_field_rejected),
    ("Unknown experience ID rejected", test_invalid_experience_id_rejected),
    ("Unsupported highlighted skill rejected", test_unsupported_skill_rejected),
    ("All validation failures logged", test_all_validation_failures_are_logged),
]


def main() -> int:
    passed = 0
    failed = 0

    original_handlers = list(logger.handlers)
    original_propagate = logger.propagate

    logger.handlers = []
    logger.propagate = False

    try:
        for test_name, test_function in TESTS:
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
    finally:
        logger.handlers = original_handlers
        logger.propagate = original_propagate

    print()
    print(f"Result: {passed} passed, {failed} failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
