from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from cv_data.models import CVProfile
from logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "cv_data" / "cv_profiles.json"


class CandidateProfileError(RuntimeError):
    """Controlled candidate profile loading failure."""


class CandidateProfileOption(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    profile_id: str = Field(min_length=1, max_length=50)
    display_name: str = Field(min_length=1, max_length=200)
    cv_path: str = Field(min_length=1, max_length=300)
    is_default: bool = False

    @property
    def absolute_cv_path(self) -> Path:
        path = Path(self.cv_path)
        return path if path.is_absolute() else PROJECT_ROOT / path


class CandidateProfileRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profiles: list[CandidateProfileOption] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_registry(self) -> "CandidateProfileRegistry":
        profile_ids = [profile.profile_id for profile in self.profiles]

        if len(profile_ids) != len(set(profile_ids)):
            raise ValueError("Candidate profile IDs must be unique.")

        if sum(1 for profile in self.profiles if profile.is_default) != 1:
            raise ValueError("Exactly one candidate profile must be default.")

        return self


def load_candidate_registry() -> CandidateProfileRegistry:
    try:
        raw_data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        return CandidateProfileRegistry.model_validate(raw_data)

    except FileNotFoundError as error:
        logger.exception("Candidate profile registry was not found.")
        raise CandidateProfileError("Candidate profile registry was not found.") from error

    except json.JSONDecodeError as error:
        logger.exception("Candidate profile registry contains invalid JSON.")
        raise CandidateProfileError("Candidate profile registry contains invalid JSON.") from error

    except ValidationError as error:
        logger.exception("Candidate profile registry is invalid.")
        raise CandidateProfileError("Candidate profile registry is invalid.") from error


def list_candidate_options() -> list[CandidateProfileOption]:
    return load_candidate_registry().profiles


def get_default_candidate_profile() -> CandidateProfileOption:
    registry = load_candidate_registry()

    for profile in registry.profiles:
        if profile.is_default:
            return profile

    raise CandidateProfileError("Default candidate profile was not found.")


def get_candidate_profile(profile_id: str) -> CandidateProfileOption:
    normalized_id = profile_id.strip()

    for profile in list_candidate_options():
        if profile.profile_id == normalized_id:
            return profile

    raise CandidateProfileError(f"Unknown candidate profile: {profile_id}")


def load_candidate_cv(profile_id: str) -> CVProfile:
    profile = get_candidate_profile(profile_id)

    try:
        raw_data = json.loads(profile.absolute_cv_path.read_text(encoding="utf-8"))
        cv = CVProfile.model_validate(raw_data)

    except FileNotFoundError as error:
        logger.exception("Candidate CV file was not found: %s", profile.profile_id)
        raise CandidateProfileError("Candidate CV file was not found.") from error

    except json.JSONDecodeError as error:
        logger.exception("Candidate CV contains invalid JSON: %s", profile.profile_id)
        raise CandidateProfileError("Candidate CV contains invalid JSON.") from error

    except ValidationError as error:
        logger.exception("Candidate CV failed validation: %s", profile.profile_id)
        raise CandidateProfileError("Candidate CV failed validation.") from error

    if cv.profile_id != profile.profile_id:
        raise CandidateProfileError("Candidate CV profile_id does not match registry.")

    return cv
