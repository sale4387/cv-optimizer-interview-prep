from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from cv_data.models import CVProfile
from logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[1]


Decision = Literal[
    "pending",
    "accepted_suggestion",
    "kept_original",
    "revision_requested",
    "revised",
]


class ReviewItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    item_id: str
    item_type: str
    source_section: str
    source_reference: str
    original_value: str
    suggested_value: str
    current_value: str
    decision: Decision = "pending"
    user_comment: str | None = None
    revision_status: str = "not_requested"


class ReviewState(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    application_id: str
    review_status: str = "in_progress"
    items: list[ReviewItem] = Field(default_factory=list)


class InlineReviewError(RuntimeError):
    """Controlled inline review preparation failure."""


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return deepcopy(value)

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="python")

    raise InlineReviewError(
        "Value cannot be converted to dictionary."
    )


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)

    return getattr(value, key, default)


def _stringify(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return "\n".join(str(item) for item in value)

    return str(value)


def _safe_id(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace("/", "_")
    )


def _load_original_cv_for_application(
    application: Any,
) -> CVProfile:
    profile_id = _get(application, "profile_id", "sale")

    try:
        from services.candidate_profile_service import load_candidate_cv

        return load_candidate_cv(profile_id)

    except Exception:
        logger.exception(
            "Candidate profile service failed; falling back to cv_data/cv_sale.json"
        )

    fallback_path = PROJECT_ROOT / "cv_data" / "cv_sale.json"

    raw_data = json.loads(
        fallback_path.read_text(encoding="utf-8")
    )

    return CVProfile.model_validate(raw_data)


def can_prepare_inline_review(
    application: Any,
) -> bool:
    return _get(application, "tailored_cv") is not None


def _add_item(
    items: list[ReviewItem],
    *,
    item_id: str,
    item_type: str,
    source_section: str,
    source_reference: str,
    original_value: Any,
    suggested_value: Any,
) -> None:
    original_text = _stringify(original_value)
    suggested_text = _stringify(suggested_value)

    if not original_text and not suggested_text:
        return

    if original_text == suggested_text:
        return

    items.append(
        ReviewItem(
            item_id=item_id,
            item_type=item_type,
            source_section=source_section,
            source_reference=source_reference,
            original_value=original_text,
            suggested_value=suggested_text,
            current_value=suggested_text,
        )
    )


def _experience_by_id(
    cv_data: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for experience in cv_data.get(
        "professional_experience",
        [],
    ):
        if isinstance(experience, dict):
            experience_id = experience.get(
                "experience_id"
            )

            if experience_id:
                result[str(experience_id)] = experience

    return result


def build_inline_review_state(
    application: Any,
) -> ReviewState:
    if not can_prepare_inline_review(application):
        raise InlineReviewError(
            "The current CV cannot be prepared for inline review because it does not contain a tailored CV."
        )

    application_id = _get(
        application,
        "application_id",
        "current-application",
    )

    original_cv = _load_original_cv_for_application(
        application
    )

    original_data = original_cv.model_dump(
        mode="python"
    )

    tailored_data = _as_dict(
        _get(application, "tailored_cv")
    )

    items: list[ReviewItem] = []

    _add_item(
        items,
        item_id="professional_summary",
        item_type="professional_summary",
        source_section="professional_summary",
        source_reference="professional_summary",
        original_value=original_data.get(
            "professional_summary"
        ),
        suggested_value=tailored_data.get(
            "professional_summary"
        ),
    )

    _add_item(
        items,
        item_id="core_skills",
        item_type="core_skills",
        source_section="core_skills",
        source_reference="core_skills",
        original_value=original_data.get(
            "core_skills",
            [],
        ),
        suggested_value=tailored_data.get(
            "core_skills",
            [],
        ),
    )

    _add_item(
        items,
        item_id="tools_and_technologies",
        item_type="tools_and_technologies",
        source_section="tools_and_technologies",
        source_reference="tools_and_technologies",
        original_value=original_data.get(
            "tools_and_technologies",
            [],
        ),
        suggested_value=tailored_data.get(
            "tools_and_technologies",
            [],
        ),
    )

    _add_item(
        items,
        item_id="projects",
        item_type="projects",
        source_section="projects",
        source_reference="projects",
        original_value=original_data.get(
            "projects",
            [],
        ),
        suggested_value=tailored_data.get(
            "projects",
            [],
        ),
    )

    original_experience = _experience_by_id(
        original_data
    )

    tailored_experience = _experience_by_id(
        tailored_data
    )

    for experience_id, tailored_item in tailored_experience.items():
        original_item = original_experience.get(
            experience_id,
            {},
        )

        original_responsibilities = original_item.get(
            "responsibilities",
            [],
        )

        tailored_responsibilities = tailored_item.get(
            "responsibilities",
            [],
        )

        max_responsibilities = max(
            len(original_responsibilities),
            len(tailored_responsibilities),
        )

        for index in range(max_responsibilities):
            _add_item(
                items,
                item_id=(
                    f"{_safe_id(experience_id)}_"
                    f"responsibility_{index + 1}"
                ),
                item_type="responsibility_bullet",
                source_section="professional_experience",
                source_reference=experience_id,
                original_value=(
                    original_responsibilities[index]
                    if index < len(original_responsibilities)
                    else ""
                ),
                suggested_value=(
                    tailored_responsibilities[index]
                    if index < len(tailored_responsibilities)
                    else ""
                ),
            )

        original_achievements = original_item.get(
            "achievements",
            [],
        )

        tailored_achievements = tailored_item.get(
            "achievements",
            [],
        )

        max_achievements = max(
            len(original_achievements),
            len(tailored_achievements),
        )

        for index in range(max_achievements):
            _add_item(
                items,
                item_id=(
                    f"{_safe_id(experience_id)}_"
                    f"achievement_{index + 1}"
                ),
                item_type="achievement_bullet",
                source_section="professional_experience",
                source_reference=experience_id,
                original_value=(
                    original_achievements[index]
                    if index < len(original_achievements)
                    else ""
                ),
                suggested_value=(
                    tailored_achievements[index]
                    if index < len(tailored_achievements)
                    else ""
                ),
            )

    logger.info(
        "Inline review state prepared: application_id=%s items=%s",
        application_id,
        len(items),
    )

    return ReviewState(
        application_id=application_id,
        items=items,
    )


def update_review_item_decision(
    review_state: ReviewState,
    *,
    item_id: str,
    decision: Decision,
    user_comment: str | None = None,
) -> ReviewState:
    updated_state = review_state.model_copy(
        deep=True
    )

    for item in updated_state.items:
        if item.item_id != item_id:
            continue

        item.decision = decision
        item.user_comment = user_comment

        if decision == "accepted_suggestion":
            item.current_value = item.suggested_value
            item.revision_status = "not_requested"

        elif decision == "kept_original":
            item.current_value = item.original_value
            item.revision_status = "not_requested"

        elif decision == "revision_requested":
            item.revision_status = "pending"

        return updated_state

    raise InlineReviewError(
        f"Review item was not found: {item_id}"
    )


def review_state_ready_to_accept(
    review_state: ReviewState,
) -> bool:
    if not review_state.items:
        return True

    return all(
        item.decision
        in {
            "accepted_suggestion",
            "kept_original",
            "revised",
        }
        for item in review_state.items
    )
