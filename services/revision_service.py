from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ai.ai_client import (
    send_gemini_request,
)
from ai.response_models import (
    CVOptimizationResponse,
)
from ai.revision_models import (
    CVRevisionRequest,
    RevisionSection,
)
from ai.validation import (
    ResponseValidationError,
    validate_cv_optimization_response,
)
from ai.workflows.cv_optimization import (
    DEFAULT_CV_PATH,
    load_cv_profile,
)
from ai.workflows.cv_revision import (
    CVRevisionWorkflowError,
    revise_cv_sections,
)
from config import settings
from cv_data.models import CVProfile
from firebase import update_application
from logger import logger
from services.application_service import (
    ApplicationResultError,
    SavedApplicationResult,
    load_saved_application,
    merge_cv_patch,
)
from services.pdf_renderer import (
    PDFRenderError,
    generate_cv_pdf,
)


EDITABLE_REVISION_SECTIONS: dict[
    RevisionSection,
    str,
] = {
    "professional_summary": (
        "Professional summary"
    ),
    "experience_updates": (
        "Professional experience"
    ),
    "skills_to_highlight": (
        "Core skills"
    ),
}

REVISION_PROMPT_VERSION = (
    "task-010-revision-v1"
)


class ApplicationRevisionError(
    RuntimeError
):
    """Controlled error for review, revision or acceptance failures."""


class DraftPDFExportError(
    ApplicationRevisionError
):
    """Raised when PDF export is requested before CV acceptance."""


def normalize_revision_comments(
    comments: Mapping[str, str],
) -> dict[RevisionSection, str]:
    normalized: dict[
        RevisionSection,
        str,
    ] = {}

    unsupported = (
        set(comments)
        - set(
            EDITABLE_REVISION_SECTIONS
        )
    )

    if unsupported:
        raise ValueError(
            "Unsupported revision sections: "
            + ", ".join(
                sorted(unsupported)
            )
        )

    for raw_section, raw_comment in (
        comments.items()
    ):
        if not isinstance(
            raw_comment,
            str,
        ):
            raise TypeError(
                "Revision comments must "
                "be strings."
            )

        cleaned_comment = (
            raw_comment.strip()
        )

        if not cleaned_comment:
            continue

        section = raw_section

        normalized[section] = (
            cleaned_comment
        )

    return normalized


def build_revision_request(
    *,
    application_id: str,
    comments: Mapping[str, str],
) -> CVRevisionRequest:
    normalized = (
        normalize_revision_comments(
            comments
        )
    )

    if not normalized:
        raise ValueError(
            "Select at least one editable "
            "section and add a comment."
        )

    return CVRevisionRequest(
        application_id=application_id,
        sections=[
            {
                "section": section,
                "comment": comment,
            }
            for (
                section,
                comment,
            ) in normalized.items()
        ],
    )


def _build_existing_optimization(
    *,
    application: (
        SavedApplicationResult
    ),
    original_cv: CVProfile,
) -> CVOptimizationResponse:
    if application.tailored_cv is None:
        raise ApplicationRevisionError(
            "This application does not "
            "contain a tailored CV."
        )

    tailored_cv = (
        application.tailored_cv
    )

    response_data = {
        "fit_assessment": (
            application
            .fit_assessment
            .model_dump(mode="python")
        ),
        "cv_patch": {
            "professional_summary": (
                tailored_cv
                .professional_summary
            ),
            "experience_updates": [
                {
                    "experience_id": (
                        experience
                        .experience_id
                    ),
                    "suggested_job_title": (
                        experience.job_title
                    ),
                    "responsibilities": list(
                        experience
                        .responsibilities
                    ),
                }
                for experience in (
                    tailored_cv
                    .professional_experience
                )
            ],
            "skills_to_highlight": list(
                tailored_cv.core_skills
            ),
        },
        "gap_analysis": (
            application
            .gap_analysis
            .model_dump(mode="python")
        ),
        "warnings": [],
    }

    try:
        return (
            validate_cv_optimization_response(
                response_data=(
                    response_data
                ),
                original_cv=original_cv,
            )
        )

    except ResponseValidationError as error:
        raise ApplicationRevisionError(
            "The current CV cannot be "
            "prepared for revision."
        ) from error


def revise_saved_application(
    *,
    application_id: str,
    comments: Mapping[str, str],
    profile_path: (
        str | Path
    ) = DEFAULT_CV_PATH,
    request_function=(
        send_gemini_request
    ),
) -> SavedApplicationResult:
    logger.info(
        "Application revision requested: "
        "application_id=%s",
        application_id,
    )

    try:
        application = (
            load_saved_application(
                application_id
            )
        )

        if application is None:
            raise ApplicationRevisionError(
                "The requested application "
                "does not exist."
            )

        if application.status != "draft":
            raise ApplicationRevisionError(
                "Only a draft CV can be revised."
            )

        revision_request = (
            build_revision_request(
                application_id=(
                    application_id
                ),
                comments=comments,
            )
        )

        original_cv_data = (
            load_cv_profile(
                profile_path
            )
        )

        original_cv = (
            CVProfile.model_validate(
                original_cv_data
            )
        )

        current_optimization = (
            _build_existing_optimization(
                application=application,
                original_cv=original_cv,
            )
        )

        assert (
            application.tailored_cv
            is not None
        )

        revised_optimization = (
            revise_cv_sections(
                original_cv=(
                    original_cv_data
                ),
                current_cv=(
                    application
                    .tailored_cv
                    .model_dump(
                        mode="python"
                    )
                ),
                current_optimization=(
                    current_optimization
                ),
                revision_request=(
                    revision_request
                ),
                request_function=(
                    request_function
                ),
            )
        )

        revised_cv = merge_cv_patch(
            original_cv=original_cv,
            optimization=(
                revised_optimization
            ),
        )

        if revised_cv is None:
            raise ApplicationRevisionError(
                "A revision unexpectedly "
                "removed the tailored CV."
            )

        update_application(
            application_id,
            {
                "status": "draft",
                "fit_assessment": (
                    revised_optimization
                    .fit_assessment
                    .model_dump(
                        mode="python"
                    )
                ),
                "tailored_cv": (
                    revised_cv.model_dump(
                        mode="python"
                    )
                ),
                "gap_analysis": (
                    revised_optimization
                    .gap_analysis
                    .model_dump(
                        mode="python"
                    )
                ),
                "prompt_version": (
                    REVISION_PROMPT_VERSION
                ),
                "model_version": (
                    settings.gemini_model
                ),
            },
        )

        saved_result = (
            load_saved_application(
                application_id
            )
        )

        if saved_result is None:
            raise ApplicationRevisionError(
                "The revised draft was saved "
                "but could not be reloaded."
            )

        logger.info(
            "Application revision completed: "
            "application_id=%s sections=%s",
            application_id,
            ", ".join(
                revision_request
                .requested_sections
            ),
        )

        return saved_result

    except (
        ApplicationRevisionError,
        ApplicationResultError,
        CVRevisionWorkflowError,
        ValidationError,
        ValueError,
        TypeError,
    ):
        logger.exception(
            "Application revision failed: "
            "application_id=%s",
            application_id,
        )
        raise

    except Exception as error:
        logger.exception(
            "Unexpected application revision "
            "failure: application_id=%s",
            application_id,
        )

        raise ApplicationRevisionError(
            "The revised draft could not "
            "be saved."
        ) from error


def accept_saved_application(
    application_id: str,
) -> SavedApplicationResult:
    logger.info(
        "Application acceptance requested: "
        "application_id=%s",
        application_id,
    )

    try:
        application = (
            load_saved_application(
                application_id
            )
        )

        if application is None:
            raise ApplicationRevisionError(
                "The requested application "
                "does not exist."
            )

        if (
            application
            .tailored_cv
            is None
        ):
            raise ApplicationRevisionError(
                "A CV must exist before "
                "it can be accepted."
            )

        if application.status == "accepted":
            return application

        update_application(
            application_id,
            {
                "status": "accepted",
            },
        )

        accepted_result = (
            load_saved_application(
                application_id
            )
        )

        if accepted_result is None:
            raise ApplicationRevisionError(
                "The accepted CV could "
                "not be reloaded."
            )

        logger.info(
            "Application accepted: "
            "application_id=%s",
            application_id,
        )

        return accepted_result

    except (
        ApplicationRevisionError,
        ApplicationResultError,
        ValueError,
        TypeError,
    ):
        logger.exception(
            "Application acceptance failed: "
            "application_id=%s",
            application_id,
        )
        raise

    except Exception as error:
        logger.exception(
            "Unexpected application acceptance "
            "failure: application_id=%s",
            application_id,
        )

        raise ApplicationRevisionError(
            "The CV could not be accepted."
        ) from error


def generate_accepted_application_pdf(
    application: SavedApplicationResult,
) -> bytes:
    if application.status != "accepted":
        logger.warning(
            "PDF export blocked for draft: "
            "application_id=%s",
            application.application_id,
        )

        raise DraftPDFExportError(
            "Accept the CV before "
            "downloading the PDF."
        )

    if application.tailored_cv is None:
        raise DraftPDFExportError(
            "This application does not "
            "contain a CV to export."
        )

    try:
        return generate_cv_pdf(
            application.tailored_cv
        )

    except PDFRenderError:
        logger.exception(
            "Accepted CV PDF generation "
            "failed: application_id=%s",
            application.application_id,
        )
        raise
