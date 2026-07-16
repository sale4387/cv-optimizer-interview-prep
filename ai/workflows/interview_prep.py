from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from typing import Any

from google import genai
from google.genai import types

from ai.cleaner import (
    CleanerError,
    clean_ai_json_response,
)
from ai.interview_prep_models import (
    InterviewPreparationReport,
)
from ai.interview_prep_validation import (
    InterviewPrepValidationError,
    validate_interview_prep_response,
)
from ai.prompts import (
    INTERVIEW_PREP_SYSTEM_INSTRUCTION,
    build_interview_prep_prompt,
)
from config import settings
from logger import logger


InterviewPrepRequestFunction = Callable[
    ...,
    str,
]


class InterviewPrepWorkflowError(
    RuntimeError
):
    """Controlled failure raised by the interview-prep workflow."""


def _send_gemini_request(
    prompt: str,
    *,
    system_instruction: str,
) -> str:
    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )

    text = getattr(
        response,
        "text",
        None,
    )

    if not text:
        raise InterviewPrepWorkflowError(
            "Gemini returned an empty interview preparation response."
        )

    return text


def generate_interview_preparation(
    *,
    application_id: str,
    original_cv: Mapping[str, Any],
    tailored_cv: Mapping[str, Any],
    job_ad: str,
    company_research: Mapping[str, Any] | None,
    request_function: InterviewPrepRequestFunction = _send_gemini_request,
) -> InterviewPreparationReport:
    generated_at = datetime.now(
        timezone.utc
    )

    logger.info(
        "Interview preparation workflow started: application_id=%s",
        application_id,
    )

    try:
        prompt = build_interview_prep_prompt(
            application_id=application_id,
            original_cv=dict(original_cv),
            tailored_cv=dict(tailored_cv),
            job_ad=job_ad,
            company_research=(
                dict(company_research)
                if company_research is not None
                else None
            ),
            generated_at=generated_at.isoformat(),
        )

        raw_response = request_function(
            prompt,
            system_instruction=(
                INTERVIEW_PREP_SYSTEM_INSTRUCTION
            ),
        )

        cleaned_response = clean_ai_json_response(
            raw_response
        )

        if not isinstance(
            cleaned_response,
            Mapping,
        ):
            raise InterviewPrepValidationError(
                [
                    "Interview preparation response must be a JSON object."
                ]
            )

        response_data: dict[str, Any] = dict(
            cleaned_response
        )

        response_data["application_id"] = (
            application_id
        )

        response_data.setdefault(
            "interview_prep_id",
            application_id,
        )

        response_data["generated_at"] = (
            generated_at.isoformat()
        )

        report = validate_interview_prep_response(
            response_data
        )

        logger.info(
            "Interview preparation workflow completed: application_id=%s status=%s questions=%s",
            application_id,
            report.prep_status,
            len(report.questions),
        )

        return report

    except (
        CleanerError,
        InterviewPrepValidationError,
        ValueError,
        TypeError,
        InterviewPrepWorkflowError,
    ) as error:
        logger.exception(
            "Interview preparation workflow failed: application_id=%s error_type=%s",
            application_id,
            type(error).__name__,
        )

        raise InterviewPrepWorkflowError(
            "Interview preparation failed safely."
        ) from error

    except Exception as error:
        logger.exception(
            "Unexpected interview preparation workflow failure: application_id=%s error_type=%s",
            application_id,
            type(error).__name__,
        )

        raise InterviewPrepWorkflowError(
            "Interview preparation failed unexpectedly."
        ) from error


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

generate_interview_preparation = observe_function(
    "interview_prep_ai_workflow"
)(generate_interview_preparation)
