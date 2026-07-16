from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from difflib import SequenceMatcher


RESULT_TERMS = (
    "achieved",
    "closed",
    "contributed",
    "delivered",
    "drove",
    "generated",
    "grew",
    "helped",
    "improved",
    "increased",
    "negotiated",
    "reduced",
    "secured",
    "supported",
    "won",
)

NUMBER_PATTERN = re.compile(
    r"(?:usd|eur|\$|€)?\s*"
    r"\d+(?:[.,]\d+)?"
    r"(?:\s*(?:%|percent|million|billion|m|k))?",
    re.IGNORECASE,
)


def _normalize(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    return re.sub(r"[^a-z0-9]+", " ", ascii_value).strip()


def _numbers(value: str) -> set[str]:
    return {
        re.sub(r"\s+", "", match.group(0).lower())
        for match in NUMBER_PATTERN.finditer(value)
    }


def _meaningful_tokens(value: str) -> set[str]:
    return {
        token
        for token in _normalize(value).split()
        if len(token) >= 4
    }


def _overlap_ratio(first: str, second: str) -> float:
    first_tokens = _meaningful_tokens(first)
    second_tokens = _meaningful_tokens(second)

    if not first_tokens or not second_tokens:
        return 0.0

    shared = first_tokens & second_tokens
    return len(shared) / min(
        len(first_tokens),
        len(second_tokens),
    )


def responsibility_duplicates_achievement(
    responsibility: str,
    achievements: Iterable[str],
) -> bool:
    normalized_responsibility = _normalize(
        responsibility
    )
    responsibility_numbers = _numbers(
        responsibility
    )
    result_word_present = any(
        term in normalized_responsibility
        for term in RESULT_TERMS
    )

    for achievement in achievements:
        normalized_achievement = _normalize(
            achievement
        )

        if not normalized_achievement:
            continue

        if (
            normalized_responsibility
            == normalized_achievement
        ):
            return True

        similarity = SequenceMatcher(
            None,
            normalized_responsibility,
            normalized_achievement,
        ).ratio()

        if similarity >= 0.72:
            return True

        shared_numbers = (
            responsibility_numbers
            & _numbers(achievement)
        )

        if shared_numbers and (
            result_word_present
            or _overlap_ratio(
                responsibility,
                achievement,
            ) >= 0.30
        ):
            return True

        if (
            result_word_present
            and _overlap_ratio(
                responsibility,
                achievement,
            ) >= 0.58
        ):
            return True

    return False


def filter_responsibilities(
    responsibilities: Iterable[str],
    achievements: Iterable[str],
) -> list[str]:
    achievement_list = [
        str(item).strip()
        for item in achievements
        if str(item).strip()
    ]

    filtered: list[str] = []

    for item in responsibilities:
        cleaned = str(item).strip()

        if not cleaned:
            continue

        if responsibility_duplicates_achievement(
            cleaned,
            achievement_list,
        ):
            continue

        filtered.append(cleaned)

    return filtered
