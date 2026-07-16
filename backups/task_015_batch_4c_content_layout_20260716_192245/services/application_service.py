from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    model_validator,
)

from ai.response_models import (
    CVOptimizationResponse,
    FitAssessment,
    GapAnalysis,
)
from ai.workflows.cv_optimization import (
    DEFAULT_CV_PATH,
    CVOptimizationWorkflowError,
    load_cv_profile,
    optimize_cv_for_role,
)
from config import settings
from cv_data.models import CVProfile
from firebase import (
    get_application,
    list_applications,
    normalize_company_key,
    save_application,
)
from logger import logger
from services.company_service import (
    CompanyResearchError,
    get_or_create_company_research,
)


SCHEMA_VERSION = "1.0"
PROMPT_VERSION = "task-007-v1"


class ApplicationResultError(RuntimeError):
    """Controlled application persistence or loading failure."""


class SavedApplicationResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    application_id: str
    profile_id: str
    company_key: str
    job_title: str
    job_ad_hash: str
    job_ad_text: str | None = None
    status: Literal["draft", "accepted"]

    fit_assessment: FitAssessment
    tailored_cv: CVProfile | None
    gap_analysis: GapAnalysis
    candidate: dict[str, Any] | None = None
    company_research: dict[str, Any] | None = None
    interview_prep: dict[str, Any] | None = None
    workflow_status: dict[str, Any] | None = None

    base_cv_version: str
    schema_version: str
    prompt_version: str
    model_version: str | None = None

    created_at: datetime
    updated_at: datetime
    accepted_at: datetime | None = None

    @model_validator(mode="after")
    def validate_fit_and_cv_consistency(
        self,
    ) -> "SavedApplicationResult":
        fit_level = self.fit_assessment.level

        if (
            fit_level == "poor"
            and self.tailored_cv is not None
        ):
            raise ValueError(
                "A poor-fit application must not contain a tailored CV."
            )

        if (
            fit_level != "poor"
            and self.tailored_cv is None
        ):
            raise ValueError(
                "An acceptable-fit application must contain a tailored CV."
            )

        return self


def _prioritize_skills(
    original_skills: list[str],
    highlighted_skills: list[str],
) -> list[str]:
    prioritized: list[str] = []
    seen: set[str] = set()

    for skill in [
        *highlighted_skills,
        *original_skills,
    ]:
        normalized = skill.strip().casefold()

        if normalized and normalized not in seen:
            seen.add(normalized)
            prioritized.append(skill.strip())

    return prioritized


def merge_cv_patch(
    *,
    original_cv: CVProfile | dict[str, Any],
    optimization: CVOptimizationResponse,
) -> CVProfile | None:
    if optimization.fit_assessment.level == "poor":
        return None

    if optimization.cv_patch is None:
        raise ValueError(
            "Acceptable fit requires a CV patch."
        )

    cv_model = (
        original_cv
        if isinstance(original_cv, CVProfile)
        else CVProfile.model_validate(original_cv)
    )

    merged_data = cv_model.model_dump(
        mode="python"
    )

    patch = optimization.cv_patch

    merged_data["professional_summary"] = (
        patch.professional_summary
    )

    merged_data["core_skills"] = (
        _prioritize_skills(
            original_skills=merged_data[
                "core_skills"
            ],
            highlighted_skills=(
                patch.skills_to_highlight
            ),
        )
    )

    updates_by_id = {
        update.experience_id: update
        for update in patch.experience_updates
    }

    for experience in merged_data[
        "professional_experience"
    ]:
        update = updates_by_id.get(
            experience["experience_id"]
        )

        if update is None:
            continue

        if update.suggested_job_title is not None:
            experience["job_title"] = (
                update.suggested_job_title
            )

        experience["responsibilities"] = list(
            update.responsibilities
        )

    return CVProfile.model_validate(merged_data)


def _build_application_payload(
    *,
    job_title: str,
    company_name: str,
    job_ad_text: str,
    original_cv: CVProfile,
    optimization: CVOptimizationResponse,
    tailored_cv: CVProfile | None,
    company_research_status: str,
    company_research_error: str | None,
) -> dict[str, Any]:
    return {
        "profile_id": original_cv.profile_id,
        "candidate": {
            "profile_id": original_cv.profile_id,
            "display_name": original_cv.personal_info.full_name,
            "base_cv_version": original_cv.cv_version,
        },
        "company_key": normalize_company_key(
            company_name
        ),
        "job_title": job_title.strip(),
        "job_ad_hash": hashlib.sha256(
            job_ad_text.strip().encode("utf-8")
        ).hexdigest(),
        "job_ad_text": job_ad_text.strip(),
        "status": "draft",
        "fit_assessment": (
            optimization
            .fit_assessment
            .model_dump(mode="python")
        ),
        "tailored_cv": (
            tailored_cv.model_dump(mode="python")
            if tailored_cv is not None
            else None
        ),
        "gap_analysis": (
            optimization
            .gap_analysis
            .model_dump(mode="python")
        ),
        "company_research": None,
        "interview_prep": None,
        "workflow_status": {
            "cv_optimization": "complete",
            "fit_assessment": "complete",
            "gap_analysis": "complete",
            "company_research": company_research_status,
            "company_research_error": company_research_error,
            "interview_prep": "not_started",
            "interview_prep_error": None,
            "pdf_export": (
                "available"
                if tailored_cv is not None
                else "blocked"
            ),
        },
        "base_cv_version": original_cv.cv_version,
        "schema_version": SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "model_version": settings.gemini_model,
    }


def load_saved_application(
    application_id: str,
) -> SavedApplicationResult | None:
    try:
        raw_record = get_application(
            application_id
        )

        if raw_record is None:
            logger.info(
                "Requested application was not found: %s",
                application_id,
            )
            return None

        result = SavedApplicationResult.model_validate(
            raw_record
        )

        logger.info(
            "Saved application loaded for UI: %s",
            application_id,
        )

        return result

    except ValidationError as error:
        logger.exception(
            "Stored application is invalid: %s",
            application_id,
        )

        raise ApplicationResultError(
            "The saved application record is invalid."
        ) from error

    except Exception as error:
        logger.exception(
            "Saved application could not be loaded: %s",
            application_id,
        )

        raise ApplicationResultError(
            "The saved application is currently unavailable."
        ) from error


def list_saved_application_results(
    profile_id: str | None = None,
) -> list[SavedApplicationResult]:
    try:
        raw_records = list_applications(
            profile_id=profile_id
        )

        results: list[SavedApplicationResult] = []

        for raw_record in raw_records:
            try:
                results.append(
                    SavedApplicationResult.model_validate(
                        raw_record
                    )
                )
            except ValidationError:
                logger.exception(
                    "Invalid application skipped in My Applications: %s",
                    raw_record.get(
                        "application_id",
                        "unknown",
                    ),
                )

        results.sort(
            key=lambda item: item.created_at,
            reverse=True,
        )

        return results

    except Exception as error:
        logger.exception(
            "Saved applications could not be listed."
        )

        raise ApplicationResultError(
            "Saved applications are currently unavailable."
        ) from error


def create_draft_application(
    *,
    job_title: str,
    company_name: str,
    job_ad_text: str,
    profile_path: str | Path = DEFAULT_CV_PATH,
) -> SavedApplicationResult:
    cleaned_job_title = job_title.strip()

    if not 1 <= len(cleaned_job_title) <= 200:
        raise ValueError(
            "Job title must contain between 1 and 200 characters."
        )

    logger.info(
        "Draft application creation started: company=%s job_title=%s",
        company_name,
        cleaned_job_title,
    )

    try:
        workflow_result = optimize_cv_for_role(
            job_ad_text=job_ad_text,
            company_name=company_name,
            profile_path=profile_path,
        )

        original_cv = CVProfile.model_validate(
            load_cv_profile(profile_path)
        )

        tailored_cv = merge_cv_patch(
            original_cv=original_cv,
            optimization=workflow_result.optimization,
        )

        company_research_status = "unavailable"
        company_research_error: str | None = None

        try:
            saved_company = get_or_create_company_research(
                company_name
            )

            company_research_status = (
                saved_company
                .company_research
                .research_status
            )

        except CompanyResearchError as error:
            company_research_error = str(error)

            logger.exception(
                "Company research failed but CV optimization "
                "will continue: company=%s",
                company_name,
            )

        payload = _build_application_payload(
            job_title=cleaned_job_title,
            company_name=company_name,
            job_ad_text=job_ad_text,
            original_cv=original_cv,
            optimization=workflow_result.optimization,
            tailored_cv=tailored_cv,
            company_research_status=company_research_status,
            company_research_error=company_research_error,
        )

        application_id = save_application(
            payload
        )

        saved_result = load_saved_application(
            application_id
        )

        if saved_result is None:
            raise ApplicationResultError(
                "The application was saved but could not be reloaded."
            )

        logger.info(
            "Draft application saved before UI display: %s",
            application_id,
        )

        return saved_result

    except (
        ValueError,
        ValidationError,
        CVOptimizationWorkflowError,
        ApplicationResultError,
    ):
        logger.exception(
            "Draft application creation failed: company=%s",
            company_name,
        )
        raise

    except Exception as error:
        logger.exception(
            "Unexpected draft application creation failure: company=%s",
            company_name,
        )

        raise ApplicationResultError(
            "The application result could not be saved."
        ) from error


# TASK-015 FIX-5 OBSERVABILITY
from observability import observe_function

create_draft_application = observe_function(
    "application_workflow"
)(create_draft_application)

load_saved_application = observe_function(
    "application_load"
)(load_saved_application)

list_saved_application_results = observe_function(
    "application_list"
)(list_saved_application_results)
