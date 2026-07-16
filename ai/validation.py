from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from ai.response_models import (
    CVOptimizationResponse,
)
from logger import logger


@dataclass(frozen=True)
class CVReferenceData:
    experience_ids: frozenset[str]
    normalized_source_text: str


class ResponseValidationError(ValueError):
    def __init__(
        self,
        reasons: list[str],
    ) -> None:
        self.reasons = tuple(reasons)

        super().__init__(
            "CV optimization response validation "
            "failed: "
            + " | ".join(reasons)
        )


def _normalize_text(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        ascii_value,
    ).strip()


def _to_plain_data(
    original_cv: BaseModel | Mapping[str, Any],
) -> dict[str, Any]:
    if isinstance(original_cv, BaseModel):
        return original_cv.model_dump(
            mode="python"
        )

    if isinstance(original_cv, Mapping):
        return dict(original_cv)

    raise TypeError(
        "original_cv must be a Pydantic model "
        "or mapping."
    )


def _collect_strings(
    value: Any,
    destination: list[str],
) -> None:
    if isinstance(value, str):
        destination.append(value)
        return

    if isinstance(value, Mapping):
        for nested_value in value.values():
            _collect_strings(
                nested_value,
                destination,
            )
        return

    if isinstance(value, list):
        for nested_value in value:
            _collect_strings(
                nested_value,
                destination,
            )


def _path_represents_experience(
    path: tuple[str, ...],
) -> bool:
    relevant_fragments = (
        "experience",
        "employment",
        "work_history",
        "work_experience",
        "career",
        "position",
    )

    joined_path = "_".join(path)

    return any(
        fragment in joined_path
        for fragment in relevant_fragments
    )


def _collect_experience_ids(
    value: Any,
    destination: set[str],
    path: tuple[str, ...] = (),
) -> None:
    if isinstance(value, Mapping):
        for raw_key, nested_value in value.items():
            key = str(raw_key).lower()
            next_path = path + (key,)

            if (
                key == "experience_id"
                and isinstance(
                    nested_value,
                    str,
                )
            ):
                destination.add(
                    nested_value.strip()
                )

            elif (
                key == "id"
                and isinstance(
                    nested_value,
                    str,
                )
                and _path_represents_experience(
                    path
                )
            ):
                destination.add(
                    nested_value.strip()
                )

            _collect_experience_ids(
                nested_value,
                destination,
                next_path,
            )

        return

    if isinstance(value, list):
        for nested_value in value:
            _collect_experience_ids(
                nested_value,
                destination,
                path,
            )


def build_cv_reference_data(
    original_cv: BaseModel | Mapping[str, Any],
) -> CVReferenceData:
    plain_cv = _to_plain_data(original_cv)

    experience_ids: set[str] = set()
    source_strings: list[str] = []

    _collect_experience_ids(
        plain_cv,
        experience_ids,
    )

    _collect_strings(
        plain_cv,
        source_strings,
    )

    normalized_source_text = _normalize_text(
        " ".join(source_strings)
    )

    return CVReferenceData(
        experience_ids=frozenset(
            experience_ids
        ),
        normalized_source_text=(
            normalized_source_text
        ),
    )


def _format_validation_error(
    error: dict[str, Any],
) -> str:
    location_parts = [
        str(part)
        for part in error.get("loc", ())
    ]

    location = ".".join(location_parts)
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


def _append_unique(
    reasons: list[str],
    reason: str,
) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _collect_model_errors(
    response_data: Mapping[str, Any],
    reasons: list[str],
) -> None:
    try:
        CVOptimizationResponse.model_validate(
            response_data
        )
    except ValidationError as error:
        for validation_error in error.errors():
            _append_unique(
                reasons,
                _format_validation_error(
                    validation_error
                ),
            )


def _collect_fit_consistency_errors(
    response_data: Mapping[str, Any],
    reasons: list[str],
) -> None:
    fit_assessment = response_data.get(
        "fit_assessment"
    )

    if not isinstance(
        fit_assessment,
        Mapping,
    ):
        return

    level = fit_assessment.get("level")

    if level not in {
        "strong",
        "solid",
        "stretch",
        "poor",
    }:
        return

    cv_patch = response_data.get("cv_patch")

    if (
        level == "poor"
        and cv_patch is not None
    ):
        _append_unique(
            reasons,
            "cv_patch must be null when "
            "fit_assessment.level is 'poor'.",
        )

    if (
        level in {
            "strong",
            "solid",
            "stretch",
        }
        and cv_patch is None
    ):
        _append_unique(
            reasons,
            "cv_patch is required when "
            f"fit_assessment.level is "
            f"'{level}'.",
        )


def _collect_reference_errors(
    response_data: Mapping[str, Any],
    reference_data: CVReferenceData,
    reasons: list[str],
) -> None:
    cv_patch = response_data.get("cv_patch")

    if not isinstance(cv_patch, Mapping):
        return

    experience_updates = cv_patch.get(
        "experience_updates"
    )

    if isinstance(experience_updates, list):
        for update_index, update in enumerate(
            experience_updates
        ):
            if not isinstance(update, Mapping):
                continue

            experience_id = update.get(
                "experience_id"
            )

            if not isinstance(
                experience_id,
                str,
            ):
                continue

            if (
                experience_id
                not in reference_data.experience_ids
            ):
                _append_unique(
                    reasons,
                    "cv_patch.experience_updates."
                    f"{update_index}.experience_id: "
                    f"'{experience_id}' does not "
                    "exist in the original CV.",
                )

    skills = cv_patch.get(
        "skills_to_highlight"
    )

    if not isinstance(skills, list):
        return

    padded_source = (
        " "
        + reference_data.normalized_source_text
        + " "
    )

    for skill_index, skill in enumerate(skills):
        if not isinstance(skill, str):
            continue

        normalized_skill = _normalize_text(skill)

        if not normalized_skill:
            continue

        if (
            f" {normalized_skill} "
            not in padded_source
        ):
            _append_unique(
                reasons,
                "cv_patch.skills_to_highlight."
                f"{skill_index}: "
                f"'{skill}' is not supported "
                "by the original CV.",
            )


def collect_validation_errors(
    response_data: Mapping[str, Any],
    original_cv: BaseModel | Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []

    if not isinstance(response_data, Mapping):
        reasons.append(
            "Response data must be a JSON object."
        )

        logger.error(
            "CV response validation failed: %s",
            " | ".join(reasons),
        )

        return reasons

    _collect_model_errors(
        response_data,
        reasons,
    )

    _collect_fit_consistency_errors(
        response_data,
        reasons,
    )

    try:
        reference_data = build_cv_reference_data(
            original_cv
        )
    except (TypeError, ValueError) as error:
        _append_unique(
            reasons,
            f"Original CV reference error: {error}",
        )
    else:
        _collect_reference_errors(
            response_data,
            reference_data,
            reasons,
        )

    if reasons:
        logger.error(
            "CV response validation failed: %s",
            " | ".join(reasons),
        )
    else:
        logger.info(
            "CV response validation completed "
            "successfully."
        )

    return reasons


def validate_cv_optimization_response(
    response_data: Mapping[str, Any],
    original_cv: BaseModel | Mapping[str, Any],
) -> CVOptimizationResponse:
    reasons = collect_validation_errors(
        response_data=response_data,
        original_cv=original_cv,
    )

    if reasons:
        raise ResponseValidationError(reasons)

    return (
        CVOptimizationResponse.model_validate(
            response_data
        )
    )


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

validate_cv_optimization_response = observe_function(
    "cv_validation"
)(validate_cv_optimization_response)
