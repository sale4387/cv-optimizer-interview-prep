from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ai.ai_client import (
    GeminiRequestError,
    send_gemini_request,
)
from ai.cleaner import CleanerError
from ai.prompts import (
    CV_REVISION_SYSTEM_INSTRUCTION,
    build_cv_revision_prompt,
)
from ai.response_models import (
    CVOptimizationResponse,
)
from ai.revision_models import (
    CVRevisionRequest,
)
from ai.revision_validation import (
    RevisionValidationError,
    clean_validate_and_merge_revision,
)
from logger import logger


GeminiRevisionRequestFunction = Callable[
    ...,
    str,
]


class CVRevisionWorkflowError(
    RuntimeError
):
    """Controlled failure raised by the targeted revision workflow."""


def revise_cv_sections(
    *,
    original_cv: Mapping[str, Any],
    current_cv: Mapping[str, Any],
    current_optimization: (
        CVOptimizationResponse
        | Mapping[str, Any]
    ),
    revision_request: CVRevisionRequest,
    request_function: (
        GeminiRevisionRequestFunction
    ) = send_gemini_request,
) -> CVOptimizationResponse:
    sections = (
        revision_request
        .requested_sections
    )

    logger.info(
        "Targeted CV revision workflow "
        "started: application_id=%s "
        "sections=%s",
        revision_request.application_id,
        ", ".join(sections),
    )

    try:
        optimization_data = (
            current_optimization
            .model_dump(mode="python")
            if isinstance(
                current_optimization,
                CVOptimizationResponse,
            )
            else dict(
                current_optimization
            )
        )

        prompt = build_cv_revision_prompt(
            original_cv=original_cv,
            current_cv=current_cv,
            current_optimization=(
                optimization_data
            ),
            revision_request=(
                revision_request
                .model_dump(mode="python")
            ),
        )

        raw_response = request_function(
            prompt,
            system_instruction=(
                CV_REVISION_SYSTEM_INSTRUCTION
            ),
        )

        merged_result = (
            clean_validate_and_merge_revision(
                raw_response=raw_response,
                request_data=revision_request,
                existing_response=(
                    current_optimization
                ),
                original_cv=original_cv,
            )
        )

        logger.info(
            "Targeted CV revision workflow "
            "completed: application_id=%s "
            "sections=%s",
            revision_request.application_id,
            ", ".join(sections),
        )

        return merged_result

    except (
        GeminiRequestError,
        CleanerError,
        RevisionValidationError,
        ValueError,
        TypeError,
    ) as error:
        logger.exception(
            "Targeted CV revision workflow "
            "failed: application_id=%s "
            "error_type=%s",
            revision_request.application_id,
            type(error).__name__,
        )

        raise CVRevisionWorkflowError(
            "The requested CV revision failed safely."
        ) from error

    except Exception as error:
        logger.exception(
            "Unexpected targeted CV revision "
            "workflow failure: "
            "application_id=%s error_type=%s",
            revision_request.application_id,
            type(error).__name__,
        )

        raise CVRevisionWorkflowError(
            "The requested CV revision failed unexpectedly."
        ) from error


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

revise_cv_sections = observe_function(
    "cv_revision_workflow"
)(revise_cv_sections)
