from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from typing import Any

from google import genai
from google.genai import types

from ai.cleaner import (
    CleanerError,
    clean_ai_json_response,
)
from ai.company_research_models import (
    CompanyResearchReport,
)
from ai.company_research_validation import (
    CompanyResearchValidationError,
    validate_company_research_response,
)
from ai.prompts import (
    COMPANY_RESEARCH_SYSTEM_INSTRUCTION,
    build_company_research_prompt,
    build_company_research_retry_prompt,
)
from config import settings
from logger import logger


GroundedRequestFunction = Callable[
    ...,
    str,
]

MAX_SCHEMA_ATTEMPTS = 2


class CompanyResearchWorkflowError(
    RuntimeError
):
    """Controlled failure raised by the company research workflow."""


def _parse_company_label(
    company_label: str,
) -> tuple[str, str, str]:
    match = re.fullmatch(
        r"\s*(.+?)\s*-\s*([A-Za-z]{2})\s*",
        company_label,
    )

    if match is None:
        raise ValueError(
            "Company label must use the format: Company Name - ISO2."
        )

    company_name, country_code = match.groups()

    ascii_name = (
        unicodedata.normalize("NFKD", company_name)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )

    normalized_name = re.sub(
        r"[^a-z0-9]+",
        "-",
        ascii_name,
    ).strip("-")

    if not normalized_name:
        raise ValueError(
            "Company name cannot be normalized."
        )

    return (
        f"{normalized_name}-{country_code.lower()}",
        company_label.strip(),
        country_code.upper(),
    )


def _send_grounded_gemini_request(
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
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ],
        ),
    )

    text = getattr(
        response,
        "text",
        None,
    )

    if not text:
        raise CompanyResearchWorkflowError(
            "Gemini returned an empty company research response."
        )

    return text


def _clean_response(
    raw_response: str,
) -> dict[str, Any]:
    cleaned_response = clean_ai_json_response(
        raw_response
    )

    if not isinstance(
        cleaned_response,
        Mapping,
    ):
        raise CompanyResearchValidationError(
            [
                "Company research response must be a JSON object."
            ]
        )

    return dict(cleaned_response)


def _add_workflow_metadata(
    response_data: Mapping[str, Any],
    *,
    company_key: str,
    display_name: str,
    country_code: str,
    generated_at: datetime,
    valid_until: datetime,
) -> dict[str, Any]:
    completed_data = dict(response_data)

    completed_data["company_key"] = company_key
    completed_data["display_name"] = display_name
    completed_data["country_code"] = country_code
    completed_data["generated_at"] = (
        generated_at.isoformat()
    )
    completed_data["valid_until"] = (
        valid_until.isoformat()
    )

    return completed_data


def _validation_reasons(
    error: Exception,
) -> list[str]:
    if isinstance(
        error,
        CompanyResearchValidationError,
    ):
        return list(error.reasons)

    return [str(error)]


def generate_company_research(
    *,
    company_label: str,
    request_function: GroundedRequestFunction = _send_grounded_gemini_request,
) -> CompanyResearchReport:
    company_key, display_name, country_code = (
        _parse_company_label(
            company_label
        )
    )

    generated_at = datetime.now(
        timezone.utc
    )

    valid_until = generated_at + timedelta(
        days=90
    )

    logger.info(
        "Company research workflow started: company_key=%s",
        company_key,
    )

    try:
        prompt = build_company_research_prompt(
            company_label=display_name,
            company_key=company_key,
            country_code=country_code,
            generated_at=generated_at.isoformat(),
            valid_until=valid_until.isoformat(),
        )

        for attempt in range(
            1,
            MAX_SCHEMA_ATTEMPTS + 1,
        ):
            raw_response = ""
            cleaned_data: dict[str, Any] | None = None

            try:
                logger.info(
                    "Company research AI attempt: company_key=%s attempt=%s/%s",
                    company_key,
                    attempt,
                    MAX_SCHEMA_ATTEMPTS,
                )

                raw_response = request_function(
                    prompt,
                    system_instruction=(
                        COMPANY_RESEARCH_SYSTEM_INSTRUCTION
                    ),
                )

                cleaned_data = _clean_response(
                    raw_response
                )

                response_data = _add_workflow_metadata(
                    cleaned_data,
                    company_key=company_key,
                    display_name=display_name,
                    country_code=country_code,
                    generated_at=generated_at,
                    valid_until=valid_until,
                )

                report = validate_company_research_response(
                    response_data
                )

                logger.info(
                    "Company research workflow completed: "
                    "company_key=%s status=%s attempts=%s",
                    company_key,
                    report.research_status,
                    attempt,
                )

                return report

            except (
                CleanerError,
                CompanyResearchValidationError,
            ) as error:
                reasons = _validation_reasons(
                    error
                )

                logger.warning(
                    "Company research response rejected: "
                    "company_key=%s attempt=%s/%s reasons=%s",
                    company_key,
                    attempt,
                    MAX_SCHEMA_ATTEMPTS,
                    " | ".join(reasons),
                )

                if attempt >= MAX_SCHEMA_ATTEMPTS:
                    raise

                prompt = build_company_research_retry_prompt(
                    company_label=display_name,
                    company_key=company_key,
                    country_code=country_code,
                    generated_at=generated_at.isoformat(),
                    valid_until=valid_until.isoformat(),
                    invalid_response=(
                        cleaned_data
                        if cleaned_data is not None
                        else raw_response
                    ),
                    validation_reasons=reasons,
                )

        raise CompanyResearchWorkflowError(
            "Company research schema retry loop ended unexpectedly."
        )

    except (
        CleanerError,
        CompanyResearchValidationError,
        ValueError,
        TypeError,
        CompanyResearchWorkflowError,
    ) as error:
        logger.exception(
            "Company research workflow failed: company_key=%s error_type=%s",
            company_key,
            type(error).__name__,
        )

        raise CompanyResearchWorkflowError(
            "Company research failed safely."
        ) from error

    except Exception as error:
        logger.exception(
            "Unexpected company research workflow failure: "
            "company_key=%s error_type=%s",
            company_key,
            type(error).__name__,
        )

        raise CompanyResearchWorkflowError(
            "Company research failed unexpectedly."
        ) from error
