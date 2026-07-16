from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from ai.ai_client import (
    GeminiRequestError,
    send_gemini_request,
)
from ai.cleaner import (
    CleanerError,
    clean_ai_json_response,
)
from ai.prompts import (
    CV_OPTIMIZATION_SYSTEM_INSTRUCTION,
    build_cv_optimization_prompt,
)
from ai.response_models import CVOptimizationResponse
from ai.validation import (
    ResponseValidationError,
    validate_cv_optimization_response,
)
from logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CV_PATH = PROJECT_ROOT / "cv_data" / "cv_sale.json"

COMPANY_LABEL_PATTERN = re.compile(
    r"^\s*.+?\s+-\s+[A-Za-z]{2}\s*$"
)

AdviceText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=20,
        max_length=500,
    ),
]

GeminiRequestFunction = Callable[..., str]


class CVOptimizationWorkflowError(RuntimeError):
    """Controlled failure raised by the CV optimization workflow."""


class CVOptimizationWorkflowResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    status: Literal["completed", "poor_fit"]
    optimization: CVOptimizationResponse
    next_step_advice: list[AdviceText] = Field(
        default_factory=list,
        max_length=5,
    )

    @model_validator(mode="after")
    def validate_status_consistency(
        self,
    ) -> "CVOptimizationWorkflowResult":
        fit_level = self.optimization.fit_assessment.level

        if self.status == "poor_fit":
            if fit_level != "poor":
                raise ValueError(
                    "poor_fit status requires a poor fit assessment."
                )

            if self.optimization.cv_patch is not None:
                raise ValueError(
                    "poor_fit status requires cv_patch to be null."
                )

            if not self.next_step_advice:
                raise ValueError(
                    "poor_fit status requires next-step advice."
                )

        if self.status == "completed" and fit_level == "poor":
            raise ValueError(
                "completed status cannot contain a poor fit assessment."
            )

        return self


def load_cv_profile(
    profile_path: str | Path = DEFAULT_CV_PATH,
) -> dict[str, Any]:
    path = Path(profile_path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise FileNotFoundError(
            f"Stored CV profile was not found: {path}"
        )

    try:
        loaded_data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Stored CV profile is not valid JSON: {path}"
        ) from error

    if not isinstance(loaded_data, dict):
        raise ValueError(
            "Stored CV profile must contain one JSON object."
        )

    logger.info(
        "Stored CV profile loaded: path=%s",
        path,
    )

    return loaded_data


def _validate_job_input(
    *,
    job_ad_text: str,
    company_name: str,
) -> tuple[str, str]:
    if not isinstance(job_ad_text, str):
        raise TypeError("job_ad_text must be a string.")

    cleaned_job_ad = job_ad_text.strip()

    if not 100 <= len(cleaned_job_ad) <= 50000:
        raise ValueError(
            "job_ad_text must contain between 100 and 50000 characters."
        )

    if not isinstance(company_name, str):
        raise TypeError("company_name must be a string.")

    cleaned_company_name = company_name.strip()

    if not COMPANY_LABEL_PATTERN.fullmatch(
        cleaned_company_name
    ):
        raise ValueError(
            "company_name must use the format: Company Name - ISO2."
        )

    return cleaned_job_ad, cleaned_company_name


def _deduplicate_advice(
    advice_items: list[str],
) -> list[str]:
    deduplicated: list[str] = []

    for item in advice_items:
        cleaned_item = item.strip()

        if (
            cleaned_item
            and cleaned_item not in deduplicated
        ):
            deduplicated.append(cleaned_item)

    return deduplicated[:5]


def _build_poor_fit_advice(
    optimization: CVOptimizationResponse,
) -> list[str]:
    advice = [
        item.preparation_recommendation
        for item in (
            optimization
            .gap_analysis
            .unsupported_requirements
        )
        if item.preparation_recommendation.strip()
    ]

    if not advice:
        missing_requirements = (
            optimization
            .fit_assessment
            .missing_requirements
        )

        if missing_requirements:
            advice.append(
                "Build credible evidence for the highest-impact missing "
                "requirements before applying to similar roles."
            )

    if not advice:
        advice.append(
            "Target roles that more closely match the experience and skills "
            "already supported by the current CV."
        )

    return _deduplicate_advice(advice)


def optimize_cv_for_role(
    *,
    job_ad_text: str,
    company_name: str,
    profile_path: str | Path = DEFAULT_CV_PATH,
    request_function: GeminiRequestFunction = send_gemini_request,
) -> CVOptimizationWorkflowResult:
    cleaned_job_ad, cleaned_company_name = (
        _validate_job_input(
            job_ad_text=job_ad_text,
            company_name=company_name,
        )
    )

    logger.info(
        "CV optimization workflow started: company=%s",
        cleaned_company_name,
    )

    try:
        cv_profile = load_cv_profile(profile_path)

        prompt = build_cv_optimization_prompt(
            cv_profile=cv_profile,
            job_ad_text=cleaned_job_ad,
            company_name=cleaned_company_name,
        )

        raw_response = request_function(
            prompt,
            system_instruction=(
                CV_OPTIMIZATION_SYSTEM_INSTRUCTION
            ),
        )

        cleaned_response = clean_ai_json_response(
            raw_response
        )

        validated_response = (
            validate_cv_optimization_response(
                response_data=cleaned_response,
                original_cv=cv_profile,
            )
        )

        if (
            validated_response
            .fit_assessment
            .level
            == "poor"
        ):
            result = CVOptimizationWorkflowResult(
                status="poor_fit",
                optimization=validated_response,
                next_step_advice=(
                    _build_poor_fit_advice(
                        validated_response
                    )
                ),
            )

            logger.info(
                "CV optimization stopped for poor fit: company=%s "
                "missing_requirements=%s",
                cleaned_company_name,
                len(
                    validated_response
                    .fit_assessment
                    .missing_requirements
                ),
            )

            return result

        result = CVOptimizationWorkflowResult(
            status="completed",
            optimization=validated_response,
        )

        logger.info(
            "CV optimization workflow completed: company=%s fit=%s",
            cleaned_company_name,
            validated_response.fit_assessment.level,
        )

        return result

    except (
        FileNotFoundError,
        ValueError,
        TypeError,
        GeminiRequestError,
        CleanerError,
        ResponseValidationError,
    ) as error:
        logger.exception(
            "CV optimization workflow failed: company=%s "
            "error_type=%s",
            cleaned_company_name,
            type(error).__name__,
        )

        raise CVOptimizationWorkflowError(
            "CV optimization workflow failed safely."
        ) from error

    except Exception as error:
        logger.exception(
            "Unexpected CV optimization workflow failure: "
            "company=%s error_type=%s",
            cleaned_company_name,
            type(error).__name__,
        )

        raise CVOptimizationWorkflowError(
            "CV optimization workflow failed unexpectedly."
        ) from error


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

optimize_cv_for_role = observe_function(
    "cv_optimization_workflow"
)(optimize_cv_for_role)
