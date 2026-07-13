from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ai.interview_prep_models import (
    InterviewPreparationReport,
)
from ai.workflows.interview_prep import (
    InterviewPrepWorkflowError,
    generate_interview_preparation,
)
from logger import logger


try:
    from firebase import update_application
except ImportError:  # pragma: no cover - handled at runtime
    update_application = None  # type: ignore[assignment]


class InterviewPrepError(
    RuntimeError
):
    """Controlled interview-preparation service failure."""


def _get_nested(
    data: Mapping[str, Any],
    path: tuple[str, ...],
) -> Any:
    current: Any = data

    for key in path:
        if not isinstance(current, Mapping):
            return None

        current = current.get(key)

    return current


def should_skip_interview_prep_for_application(
    application_record: Mapping[str, Any],
) -> bool:
    possible_fit_paths = (
        ("fit_assessment", "level"),
        ("workflow_result", "fit_assessment", "level"),
        ("optimization_result", "fit_assessment", "level"),
        ("result", "fit_assessment", "level"),
    )

    for path in possible_fit_paths:
        level = _get_nested(
            application_record,
            path,
        )

        if isinstance(level, str):
            return level.lower() == "poor"

    return False


def generate_interview_prep_report(
    *,
    application_id: str,
    original_cv: Mapping[str, Any],
    tailored_cv: Mapping[str, Any],
    job_ad: str,
    company_research: Mapping[str, Any] | None,
    request_function=None,
) -> InterviewPreparationReport:
    try:
        return generate_interview_preparation(
            application_id=application_id,
            original_cv=original_cv,
            tailored_cv=tailored_cv,
            job_ad=job_ad,
            company_research=company_research,
            **(
                {"request_function": request_function}
                if request_function is not None
                else {}
            ),
        )

    except InterviewPrepWorkflowError:
        logger.exception(
            "Interview preparation report generation failed: application_id=%s",
            application_id,
        )
        raise

    except Exception as error:
        logger.exception(
            "Unexpected interview preparation service failure: application_id=%s",
            application_id,
        )

        raise InterviewPrepError(
            "Interview preparation is currently unavailable."
        ) from error


def attach_interview_prep_to_application(
    *,
    application_id: str,
    interview_prep: InterviewPreparationReport,
) -> None:
    if update_application is None:
        raise InterviewPrepError(
            "Application update function is not available."
        )

    updates = {
        "interview_prep": interview_prep.model_dump(
            mode="python"
        )
    }

    try:
        try:
            update_application(
                application_id=application_id,
                updates=updates,
            )

        except TypeError:
            update_application(
                application_id,
                updates,
            )

    except Exception as error:
        logger.exception(
            "Interview preparation save failed: application_id=%s",
            application_id,
        )

        raise InterviewPrepError(
            "Interview preparation could not be saved."
        ) from error


def generate_and_store_interview_prep(
    *,
    application_id: str,
    original_cv: Mapping[str, Any],
    tailored_cv: Mapping[str, Any],
    job_ad: str,
    company_research: Mapping[str, Any] | None,
    request_function=None,
) -> InterviewPreparationReport:
    report = generate_interview_prep_report(
        application_id=application_id,
        original_cv=original_cv,
        tailored_cv=tailored_cv,
        job_ad=job_ad,
        company_research=company_research,
        request_function=request_function,
    )

    attach_interview_prep_to_application(
        application_id=application_id,
        interview_prep=report,
    )

    logger.info(
        "Interview preparation generated and stored: application_id=%s",
        application_id,
    )

    return report
