from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from ai.company_research_models import (
    CompanyResearchReport,
)
from logger import logger


class CompanyResearchValidationError(
    ValueError
):
    def __init__(
        self,
        reasons: list[str],
    ) -> None:
        self.reasons = tuple(reasons)

        super().__init__(
            "Company research validation failed: "
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


def collect_company_research_errors(
    response_data: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []

    if not isinstance(
        response_data,
        Mapping,
    ):
        reasons.append(
            "Company research response must be a JSON object."
        )
        return reasons

    try:
        CompanyResearchReport.model_validate(
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
            "Company research validation failed: %s",
            " | ".join(reasons),
        )

    else:
        logger.info(
            "Company research validation completed successfully."
        )

    return reasons


def validate_company_research_response(
    response_data: Mapping[str, Any],
) -> CompanyResearchReport:
    reasons = collect_company_research_errors(
        response_data
    )

    if reasons:
        raise CompanyResearchValidationError(
            reasons
        )

    return CompanyResearchReport.model_validate(
        response_data
    )


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

validate_company_research_response = observe_function(
    "company_research_validation"
)(validate_company_research_response)
