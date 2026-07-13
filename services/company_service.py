from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
)

from ai.company_research_models import (
    CompanyResearchReport,
)
from ai.workflows.company_research import (
    CompanyResearchWorkflowError,
    generate_company_research,
)
from config import settings
from firebase import (
    get_company,
    get_company_by_key,
    list_companies,
    normalize_company_key,
    save_company,
)
from logger import logger


COMPANY_RESEARCH_SCHEMA_VERSION = "1.0"
COMPANY_RESEARCH_PROMPT_VERSION = (
    "task-012-company-research-v1"
)


class CompanyResearchError(
    RuntimeError
):
    """Controlled company research service failure."""


class SavedCompanyResearch(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    company_key: str
    display_name: str
    company_research: CompanyResearchReport
    schema_version: str
    prompt_version: str
    model_version: str | None = None
    created_at: datetime
    updated_at: datetime


def _build_saved_company_research(
    raw_record: dict[str, Any],
) -> SavedCompanyResearch:
    data = dict(raw_record)

    data["company_research"] = (
        CompanyResearchReport.model_validate(
            raw_record["company_research"]
        )
    )

    return SavedCompanyResearch.model_validate(
        data
    )


def _is_reusable(
    saved: SavedCompanyResearch,
) -> bool:
    now = datetime.now(timezone.utc)

    valid_until = saved.company_research.valid_until

    if valid_until.tzinfo is None:
        valid_until = valid_until.replace(
            tzinfo=timezone.utc
        )

    return valid_until > now


def get_or_create_company_research(
    company_label: str,
    *,
    request_function=None,
) -> SavedCompanyResearch:
    company_key = normalize_company_key(
        company_label
    )

    logger.info(
        "Company research requested: company_key=%s",
        company_key,
    )

    try:
        existing_record = get_company(
            company_label
        )

        if existing_record is not None:
            saved = _build_saved_company_research(
                existing_record
            )

            if _is_reusable(saved):
                logger.info(
                    "Company research cache hit: company_key=%s",
                    company_key,
                )

                return saved

            logger.info(
                "Company research expired and will be refreshed: company_key=%s",
                company_key,
            )

        report = generate_company_research(
            company_label=company_label,
            **(
                {"request_function": request_function}
                if request_function is not None
                else {}
            ),
        )

        save_company(
            company_label=company_label,
            company_research=report.model_dump(
                mode="python"
            ),
            schema_version=(
                COMPANY_RESEARCH_SCHEMA_VERSION
            ),
            prompt_version=(
                COMPANY_RESEARCH_PROMPT_VERSION
            ),
            model_version=settings.gemini_model,
        )

        refreshed_record = get_company(
            company_label
        )

        if refreshed_record is None:
            raise CompanyResearchError(
                "Company research was saved but could not be reloaded."
            )

        saved = _build_saved_company_research(
            refreshed_record
        )

        logger.info(
            "Company research saved and loaded: company_key=%s",
            company_key,
        )

        return saved

    except (
        CompanyResearchError,
        CompanyResearchWorkflowError,
        ValidationError,
        ValueError,
        TypeError,
    ):
        logger.exception(
            "Company research service failed: company_key=%s",
            company_key,
        )
        raise

    except Exception as error:
        logger.exception(
            "Unexpected company research service failure: company_key=%s",
            company_key,
        )

        raise CompanyResearchError(
            "Company research is currently unavailable."
        ) from error


def load_saved_company_research(
    company_key: str,
) -> SavedCompanyResearch | None:
    try:
        raw_record = get_company_by_key(
            company_key
        )

        if raw_record is None:
            return None

        return _build_saved_company_research(
            raw_record
        )

    except (
        ValidationError,
        ValueError,
        TypeError,
    ) as error:
        logger.exception(
            "Stored company research is invalid: company_key=%s",
            company_key,
        )

        raise CompanyResearchError(
            "The saved company research record is invalid."
        ) from error

    except Exception as error:
        logger.exception(
            "Saved company research could not be loaded: company_key=%s",
            company_key,
        )

        raise CompanyResearchError(
            "Saved company research is currently unavailable."
        ) from error


def list_saved_company_research(
) -> list[SavedCompanyResearch]:
    try:
        records = list_companies()

        results: list[
            SavedCompanyResearch
        ] = []

        for record in records:
            try:
                results.append(
                    _build_saved_company_research(
                        record
                    )
                )
            except ValidationError:
                logger.exception(
                    "Invalid company research skipped: %s",
                    record.get(
                        "company_key",
                        "unknown",
                    ),
                )

        results.sort(
            key=lambda item: item.updated_at,
            reverse=True,
        )

        return results

    except Exception as error:
        logger.exception(
            "Company research list failed."
        )

        raise CompanyResearchError(
            "Company reports are currently unavailable."
        ) from error
