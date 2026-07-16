from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from ai.interview_prep_models import (
    InterviewPreparationReport,
)
from logger import logger


class InterviewPrepValidationError(
    ValueError
):
    def __init__(
        self,
        reasons: list[str],
    ) -> None:
        self.reasons = tuple(reasons)

        super().__init__(
            "Interview preparation validation failed: "
            + " | ".join(reasons)
        )


def _format_validation_error(
    error: dict[str, Any],
) -> str:
    location = ".".join(
        str(part)
        for part in error.get("loc", ())
    )

    message = str(
        error.get(
            "msg",
            "Invalid value",
        )
    )

    if message.startswith("Value error, "):
        message = message.removeprefix(
            "Value error, "
        )

    if not location:
        return message

    return f"{location}: {message}"


def collect_interview_prep_errors(
    response_data: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []

    if not isinstance(
        response_data,
        Mapping,
    ):
        reasons.append(
            "Interview preparation response must be a JSON object."
        )
        return reasons

    try:
        InterviewPreparationReport.model_validate(
            response_data
        )

    except ValidationError as error:
        for item in error.errors():
            reason = _format_validation_error(
                item
            )

            if reason not in reasons:
                reasons.append(reason)

    if reasons:
        logger.error(
            "Interview preparation validation failed: %s",
            " | ".join(reasons),
        )

    else:
        logger.info(
            "Interview preparation validation completed successfully."
        )

    return reasons


def validate_interview_prep_response(
    response_data: Mapping[str, Any],
) -> InterviewPreparationReport:
    reasons = collect_interview_prep_errors(
        response_data
    )

    if reasons:
        raise InterviewPrepValidationError(
            reasons
        )

    return InterviewPreparationReport.model_validate(
        response_data
    )
