from __future__ import annotations

import json
import re
from typing import Any

from logger import logger


MARKDOWN_JSON_BLOCK = re.compile(
    r"```(?:json)?\s*(.*?)```",
    flags=re.IGNORECASE | re.DOTALL,
)


class CleanerError(ValueError):
    """Raised when no valid JSON object can be extracted."""


def _extract_json_object(
    candidate: str,
) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()

    for index, character in enumerate(candidate):
        if character != "{":
            continue

        try:
            parsed_value, _ = decoder.raw_decode(
                candidate[index:]
            )
        except json.JSONDecodeError:
            continue

        if isinstance(parsed_value, dict):
            return parsed_value

    return None


def clean_ai_json_response(
    raw_response: str,
) -> dict[str, Any]:
    if not isinstance(raw_response, str):
        message = (
            "AI response cleaner expected a string."
        )
        logger.error(message)
        raise CleanerError(message)

    stripped_response = raw_response.strip()

    if not stripped_response:
        message = "AI response is empty."
        logger.error(message)
        raise CleanerError(message)

    candidates: list[str] = []

    for match in MARKDOWN_JSON_BLOCK.finditer(
        stripped_response
    ):
        fenced_content = match.group(1).strip()

        if fenced_content:
            candidates.append(fenced_content)

    candidates.append(stripped_response)

    for candidate in candidates:
        parsed_object = _extract_json_object(
            candidate
        )

        if parsed_object is not None:
            logger.info(
                "AI response cleaned and parsed "
                "successfully."
            )
            return parsed_object

    message = (
        "AI response does not contain a valid "
        "JSON object."
    )

    logger.error(
        "AI response cleaner failed: %s",
        message,
    )

    raise CleanerError(message)
