from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ai.workflows.interview_prep import (
    InterviewPrepWorkflowError,
    generate_interview_preparation,
)
from firebase import update_application
from logger import logger
from services.candidate_profile_service import (
    CandidateProfileError,
    load_candidate_cv,
)
from services.company_service import (
    CompanyResearchError,
    load_saved_company_research,
)


INTERVIEW_PREP_SCHEMA_VERSION = (
    "application-interview-prep-v2"
)
INTERVIEW_PREP_PROMPT_VERSION = (
    "task-015-fix-1b-v1"
)

GENERIC_FRAGMENTS = (
    "this tests whether the candidate can connect their background",
    "use only examples already present",
    "open with the strongest matching experience",
    "use one concrete account or client example",
    "explain a structured approach",
    "do not add new claims",
    "use confirmed account management",
    "use fit/gap analysis if available",
)


class InterviewPrepServiceError(
    RuntimeError
):
    """Controlled application interview-prep failure."""


def _to_dict(
    value: Any,
) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return dict(value)

    if hasattr(value, "model_dump"):
        try:
            return value.model_dump(
                mode="python"
            )
        except TypeError:
            return value.model_dump()
        except Exception:
            pass

    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass

    return {}


def get_existing_interview_prep(
    application: Any,
) -> dict[str, Any] | None:
    app = _to_dict(application)

    for key in (
        "interview_prep",
        "interview_preparation",
        "application_interview_prep",
    ):
        value = app.get(key)

        if isinstance(value, dict):
            return dict(value)

    return None


def _is_current_prep(
    prep: Mapping[str, Any],
) -> bool:
    questions = prep.get("questions")
    candidate_questions = prep.get(
        "candidate_questions_to_ask"
    )

    return (
        prep.get("schema_version")
        == INTERVIEW_PREP_SCHEMA_VERSION
        and prep.get("prep_status")
        == "complete"
        and isinstance(questions, list)
        and 10 <= len(questions) <= 15
        and isinstance(candidate_questions, list)
        and len(candidate_questions) >= 3
    )


def _flatten_strings(
    value: Any,
) -> list[str]:
    strings: list[str] = []

    if isinstance(value, str):
        cleaned = value.strip()

        if cleaned:
            strings.append(cleaned)

    elif isinstance(value, Mapping):
        for nested in value.values():
            strings.extend(
                _flatten_strings(nested)
            )

    elif isinstance(value, list):
        for nested in value:
            strings.extend(
                _flatten_strings(nested)
            )

    return strings


def _collect_personalization_issues(
    prep: Mapping[str, Any],
    *,
    company_key: str,
    job_title: str,
    original_cv: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    questions = prep.get("questions")

    if not isinstance(questions, list):
        return [
            "Interview preparation questions are missing."
        ]

    all_text = " ".join(
        _flatten_strings(prep)
    ).lower()

    for fragment in GENERIC_FRAGMENTS:
        if fragment in all_text:
            issues.append(
                "Generic template wording detected: "
                f"{fragment}"
            )

    anchor_terms: set[str] = set()

    for value in (
        company_key.replace("-", " "),
        job_title,
    ):
        for term in value.lower().split():
            cleaned = term.strip(".,/()-")

            if len(cleaned) >= 4:
                anchor_terms.add(cleaned)

    experiences = original_cv.get(
        "professional_experience",
        [],
    )

    if isinstance(experiences, list):
        for experience in experiences:
            if not isinstance(
                experience,
                Mapping,
            ):
                continue

            for field_name in (
                "employer",
                "job_title",
            ):
                value = experience.get(
                    field_name
                )

                if isinstance(value, str):
                    for term in value.lower().split():
                        cleaned = term.strip(
                            ".,/()-"
                        )

                        if len(cleaned) >= 4:
                            anchor_terms.add(
                                cleaned
                            )

    anchored_questions = 0
    evidence_questions = 0
    answer_draft_questions = 0

    for question in questions:
        if not isinstance(
            question,
            Mapping,
        ):
            continue

        question_text = " ".join(
            _flatten_strings(question)
        ).lower()

        if any(
            term in question_text
            for term in anchor_terms
        ):
            anchored_questions += 1

        evidence = question.get(
            "evidence_to_use"
        )

        if (
            isinstance(evidence, list)
            and any(
                isinstance(item, str)
                and len(item.strip()) >= 25
                and not any(
                    fragment in item.lower()
                    for fragment in GENERIC_FRAGMENTS
                )
                for item in evidence
            )
        ):
            evidence_questions += 1

        directions = question.get(
            "suggested_answer_directions"
        )

        if isinstance(directions, list):
            for direction in directions:
                if not isinstance(
                    direction,
                    Mapping,
                ):
                    continue

                draft = direction.get(
                    "example_focus"
                )

                if (
                    isinstance(draft, str)
                    and len(draft.strip()) >= 80
                ):
                    answer_draft_questions += 1
                    break

    required = min(8, len(questions))

    if anchored_questions < required:
        issues.append(
            "Too few questions contain concrete "
            "company, role or CV anchors."
        )

    if evidence_questions < required:
        issues.append(
            "Too few questions contain concrete CV evidence."
        )

    if answer_draft_questions < required:
        issues.append(
            "Too few questions contain usable answer drafts."
        )

    return issues


def _load_company_context(
    application: Mapping[str, Any],
) -> dict[str, Any] | None:
    embedded = application.get(
        "company_research"
    )

    if isinstance(embedded, Mapping):
        return dict(embedded)

    company_key = application.get(
        "company_key"
    )

    if not isinstance(company_key, str):
        return None

    try:
        saved = load_saved_company_research(
            company_key
        )

    except CompanyResearchError:
        logger.exception(
            "Company intelligence unavailable for interview prep: "
            "company_key=%s",
            company_key,
        )
        return None

    if saved is None:
        return None

    return saved.company_research.model_dump(
        mode="python"
    )


def _limited_result(
    *,
    application_id: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "schema_version": (
            INTERVIEW_PREP_SCHEMA_VERSION
        ),
        "prompt_version": (
            INTERVIEW_PREP_PROMPT_VERSION
        ),
        "scope": "application",
        "application_id": application_id,
        "prep_status": "limited",
        "reason": reason,
        "questions": [],
        "candidate_questions_to_ask": [],
        "limitations": [reason],
    }


def _save_interview_result(
    *,
    application: Mapping[str, Any],
    prep: dict[str, Any],
) -> None:
    application_id = str(
        application.get("application_id")
        or ""
    ).strip()

    workflow_status = dict(
        application.get("workflow_status")
        or {}
    )

    prep_status = str(
        prep.get("prep_status")
        or "limited"
    )

    workflow_status[
        "interview_prep"
    ] = prep_status

    workflow_status[
        "interview_prep_error"
    ] = (
        None
        if prep_status == "complete"
        else prep.get("reason")
    )

    update_application(
        application_id,
        {
            "interview_prep": prep,
            "workflow_status": workflow_status,
        },
    )


def generate_application_interview_prep(
    application: Any,
) -> dict[str, Any]:
    app = _to_dict(application)

    application_id = str(
        app.get("application_id")
        or ""
    ).strip()

    existing = get_existing_interview_prep(
        app
    )

    if (
        existing is not None
        and _is_current_prep(existing)
    ):
        return existing

    job_ad_text = app.get(
        "job_ad_text"
    )

    if not isinstance(
        job_ad_text,
        str,
    ) or len(job_ad_text.strip()) < 100:
        result = _limited_result(
            application_id=(
                application_id
                or "unknown"
            ),
            reason=(
                "This older application does not contain "
                "the stored job advertisement."
            ),
        )

        if application_id:
            _save_interview_result(
                application=app,
                prep=result,
            )

        return result

    profile_id = str(
        app.get("profile_id")
        or ""
    ).strip()

    tailored_cv = _to_dict(
        app.get("tailored_cv")
    )

    if not (
        application_id
        and profile_id
        and tailored_cv
    ):
        raise InterviewPrepServiceError(
            "Application context is incomplete."
        )

    try:
        original_cv = load_candidate_cv(
            profile_id
        ).model_dump(
            mode="python"
        )

        company_research = _load_company_context(
            app
        )

        last_issues: list[str] = []
        last_error: Exception | None = None

        for attempt in range(1, 3):
            try:
                report = (
                    generate_interview_preparation(
                        application_id=application_id,
                        original_cv=original_cv,
                        tailored_cv=tailored_cv,
                        job_ad=job_ad_text.strip(),
                        company_research=company_research,
                    )
                )

            except InterviewPrepWorkflowError as error:
                last_error = error

                logger.warning(
                    "Interview prep generation attempt failed: "
                    "application_id=%s attempt=%s",
                    application_id,
                    attempt,
                )
                continue

            prep = report.model_dump(
                mode="json"
            )
            prep["schema_version"] = (
                INTERVIEW_PREP_SCHEMA_VERSION
            )
            prep["prompt_version"] = (
                INTERVIEW_PREP_PROMPT_VERSION
            )
            prep["scope"] = "application"
            prep["quality_attempt"] = attempt

            last_issues = (
                _collect_personalization_issues(
                    prep,
                    company_key=str(
                        app.get("company_key")
                        or ""
                    ),
                    job_title=str(
                        app.get("job_title")
                        or ""
                    ),
                    original_cv=original_cv,
                )
            )

            if not last_issues:
                _save_interview_result(
                    application=app,
                    prep=prep,
                )

                logger.info(
                    "Personalized interview prep saved: "
                    "application_id=%s questions=%s attempt=%s",
                    application_id,
                    len(
                        prep.get(
                            "questions",
                            [],
                        )
                    ),
                    attempt,
                )

                return prep

            logger.warning(
                "Interview prep quality check failed: "
                "application_id=%s attempt=%s issues=%s",
                application_id,
                attempt,
                " | ".join(last_issues),
            )

        reason = (
            "Interview preparation did not pass "
            "the personalization quality check."
        )

        if last_issues:
            reason += (
                " "
                + " | ".join(last_issues)
            )

        elif last_error is not None:
            reason += (
                " Generation failed after "
                "two controlled attempts."
            )

        result = _limited_result(
            application_id=application_id,
            reason=reason,
        )

        _save_interview_result(
            application=app,
            prep=result,
        )

        return result

    except (
        CandidateProfileError,
        CompanyResearchError,
        ValueError,
        TypeError,
    ) as error:
        logger.exception(
            "Interview preparation service failed: "
            "application_id=%s",
            application_id,
        )

        result = _limited_result(
            application_id=application_id,
            reason=(
                "Interview preparation is currently unavailable: "
                f"{type(error).__name__}"
            ),
        )

        _save_interview_result(
            application=app,
            prep=result,
        )

        return result


# TASK-015 BATCH-1 OBSERVABILITY
from observability import observe_function

generate_application_interview_prep = observe_function(
    "interview_prep_service"
)(
    generate_application_interview_prep
)
