from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import (
    BaseModel,
    ValidationError,
)

from ai.cleaner import (
    clean_ai_json_response,
)
from ai.response_models import (
    CVOptimizationResponse,
)
from ai.revision_models import (
    CVRevisionRequest,
    CVRevisionResponse,
)
from ai.validation import (
    ResponseValidationError,
    validate_cv_optimization_response,
)
from logger import logger


ALLOWED_REVISION_SECTIONS = {
    "professional_summary",
    "experience_updates",
    "skills_to_highlight",
}


class RevisionValidationError(
    ValueError
):
    def __init__(
        self,
        reasons: list[str],
    ) -> None:
        self.reasons = tuple(reasons)

        super().__init__(
            "CV revision validation failed: "
            + " | ".join(reasons)
        )


def _append_unique(
    reasons: list[str],
    reason: str,
) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _format_pydantic_error(
    error: dict[str, Any],
) -> str:
    location = ".".join(
        str(part)
        for part in error.get(
            "loc",
            (),
        )
    )

    message = str(
        error.get(
            "msg",
            "Invalid value",
        )
    )

    if message.startswith(
        "Value error, "
    ):
        message = message.removeprefix(
            "Value error, "
        )

    if not location:
        return message

    return f"{location}: {message}"


def _collect_pydantic_errors(
    model: type[BaseModel],
    data: Any,
    prefix: str,
    reasons: list[str],
) -> BaseModel | None:
    try:
        return model.model_validate(data)

    except ValidationError as error:
        for item in error.errors():
            formatted = (
                _format_pydantic_error(
                    item
                )
            )

            _append_unique(
                reasons,
                f"{prefix}: {formatted}",
            )

        return None


def _log_and_raise(
    reasons: list[str],
) -> None:
    logger.error(
        "CV revision validation failed: %s",
        " | ".join(reasons),
    )

    raise RevisionValidationError(
        reasons
    )


def collect_revision_validation_errors(
    *,
    request_data: (
        CVRevisionRequest
        | Mapping[str, Any]
    ),
    response_data: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []

    request_model = (
        request_data
        if isinstance(
            request_data,
            CVRevisionRequest,
        )
        else _collect_pydantic_errors(
            CVRevisionRequest,
            request_data,
            "revision_request",
            reasons,
        )
    )

    if not isinstance(
        response_data,
        Mapping,
    ):
        _append_unique(
            reasons,
            "revision_response: response "
            "must be a JSON object.",
        )

        return reasons

    response_keys = {
        str(key)
        for key in response_data.keys()
    }

    unsupported_keys = (
        response_keys
        - ALLOWED_REVISION_SECTIONS
    )

    for key in sorted(
        unsupported_keys
    ):
        _append_unique(
            reasons,
            "revision_response: unexpected "
            f"section '{key}'.",
        )

    if isinstance(
        request_model,
        CVRevisionRequest,
    ):
        requested = set(
            request_model
            .requested_sections
        )

        missing = (
            requested
            - response_keys
        )

        additional = (
            response_keys
            - requested
        )

        for section in sorted(
            missing
        ):
            _append_unique(
                reasons,
                "revision_response: requested "
                f"section '{section}' is missing.",
            )

        for section in sorted(
            additional
        ):
            _append_unique(
                reasons,
                "revision_response: section "
                f"'{section}' was not requested.",
            )

    _collect_pydantic_errors(
        CVRevisionResponse,
        response_data,
        "revision_response",
        reasons,
    )

    if reasons:
        logger.error(
            "CV revision validation failed: %s",
            " | ".join(reasons),
        )
    else:
        logger.info(
            "CV revision response passed "
            "section validation."
        )

    return reasons


def validate_revision_response(
    *,
    request_data: (
        CVRevisionRequest
        | Mapping[str, Any]
    ),
    response_data: Mapping[str, Any],
) -> tuple[
    CVRevisionRequest,
    CVRevisionResponse,
]:
    reasons = (
        collect_revision_validation_errors(
            request_data=request_data,
            response_data=response_data,
        )
    )

    if reasons:
        _log_and_raise(reasons)

    request_model = (
        request_data
        if isinstance(
            request_data,
            CVRevisionRequest,
        )
        else CVRevisionRequest.model_validate(
            request_data
        )
    )

    response_model = (
        CVRevisionResponse.model_validate(
            response_data
        )
    )

    return (
        request_model,
        response_model,
    )


def validate_and_merge_revision(
    *,
    request_data: (
        CVRevisionRequest
        | Mapping[str, Any]
    ),
    response_data: Mapping[str, Any],
    existing_response: (
        CVOptimizationResponse
        | Mapping[str, Any]
    ),
    original_cv: (
        BaseModel
        | Mapping[str, Any]
    ),
) -> CVOptimizationResponse:
    reasons: list[str] = []

    try:
        (
            request_model,
            revision_model,
        ) = validate_revision_response(
            request_data=request_data,
            response_data=response_data,
        )

    except RevisionValidationError as error:
        reasons.extend(error.reasons)
        _log_and_raise(reasons)

    existing_model = (
        existing_response
        if isinstance(
            existing_response,
            CVOptimizationResponse,
        )
        else _collect_pydantic_errors(
            CVOptimizationResponse,
            existing_response,
            "existing_response",
            reasons,
        )
    )

    if not isinstance(
        existing_model,
        CVOptimizationResponse,
    ):
        _log_and_raise(reasons)

    if existing_model.cv_patch is None:
        _append_unique(
            reasons,
            "existing_response: CV sections "
            "cannot be revised when cv_patch "
            "is null.",
        )

        _log_and_raise(reasons)

    merged_data = (
        existing_model.model_dump(
            mode="python"
        )
    )

    merged_patch = dict(
        merged_data["cv_patch"]
    )

    for section in (
        request_model
        .requested_sections
    ):
        value = getattr(
            revision_model,
            section,
        )

        if isinstance(value, list):
            merged_patch[section] = [
                (
                    item.model_dump(
                        mode="python"
                    )
                    if isinstance(
                        item,
                        BaseModel,
                    )
                    else item
                )
                for item in value
            ]
        else:
            merged_patch[section] = value

    merged_data["cv_patch"] = (
        merged_patch
    )

    try:
        merged_model = (
            validate_cv_optimization_response(
                response_data=merged_data,
                original_cv=original_cv,
            )
        )

    except ResponseValidationError as error:
        for reason in error.reasons:
            _append_unique(
                reasons,
                "merged_response: "
                f"{reason}",
            )

        logger.error(
            "CV revision merge failed: %s",
            " | ".join(reasons),
        )

        raise RevisionValidationError(
            reasons
        ) from error

    except Exception as error:
        _append_unique(
            reasons,
            "merged_response: complete "
            f"validation failed: {error}",
        )

        logger.exception(
            "Unexpected CV revision merge "
            "failure."
        )

        raise RevisionValidationError(
            reasons
        ) from error

    logger.info(
        "CV revision validated and merged: "
        "application_id=%s sections=%s",
        request_model.application_id,
        ", ".join(
            request_model
            .requested_sections
        ),
    )

    return merged_model


def clean_validate_and_merge_revision(
    *,
    raw_response: str,
    request_data: (
        CVRevisionRequest
        | Mapping[str, Any]
    ),
    existing_response: (
        CVOptimizationResponse
        | Mapping[str, Any]
    ),
    original_cv: (
        BaseModel
        | Mapping[str, Any]
    ),
) -> CVOptimizationResponse:
    cleaned_response = (
        clean_ai_json_response(
            raw_response
        )
    )

    return validate_and_merge_revision(
        request_data=request_data,
        response_data=cleaned_response,
        existing_response=existing_response,
        original_cv=original_cv,
    )
