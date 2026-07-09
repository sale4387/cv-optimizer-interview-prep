from __future__ import annotations

import time
from functools import lru_cache

import httpx
from google import genai
from google.genai import errors, types

from ai.prompts import BASE_SYSTEM_INSTRUCTION
from config import settings
from logger import logger


RETRYABLE_STATUS_CODES = {
    408,
    429,
    500,
    502,
    503,
    504,
}


class GeminiRequestError(RuntimeError):
    """Controlled failure returned when Gemini processing cannot complete."""


class EmptyGeminiResponseError(RuntimeError):
    """Raised when Gemini returns no usable text."""


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    timeout_milliseconds = int(
        settings.gemini_timeout_seconds * 1000
    )

    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=timeout_milliseconds,
            retry_options=types.HttpRetryOptions(
                attempts=1,
            ),
        ),
    )

    logger.info(
        "Gemini client initialized: model=%s timeout_seconds=%s",
        settings.gemini_model,
        settings.gemini_timeout_seconds,
    )

    return client


def _is_retryable_api_error(
    error: errors.APIError,
) -> bool:
    return error.code in RETRYABLE_STATUS_CODES


def send_gemini_request(
    prompt: str,
    *,
    system_instruction: str = BASE_SYSTEM_INSTRUCTION,
) -> str:
    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("Gemini prompt cannot be empty.")

    max_attempts = min(
        max(settings.gemini_max_attempts, 1),
        3,
    )

    client = get_gemini_client()
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        retryable = False
        current_error: Exception

        try:
            logger.info(
                "Sending Gemini request: attempt=%s/%s model=%s",
                attempt,
                max_attempts,
                settings.gemini_model,
            )

            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=cleaned_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=(
                        settings.gemini_max_output_tokens
                    ),
                ),
            )

            response_text = (
                response.text or ""
            ).strip()

            if not response_text:
                raise EmptyGeminiResponseError(
                    "Gemini returned an empty response."
                )

            logger.info(
                "Gemini request completed: attempt=%s/%s",
                attempt,
                max_attempts,
            )

            return response_text

        except EmptyGeminiResponseError as error:
            current_error = error
            retryable = True

        except errors.APIError as error:
            current_error = error
            retryable = _is_retryable_api_error(error)

        except (
            httpx.TimeoutException,
            httpx.TransportError,
            TimeoutError,
            ConnectionError,
        ) as error:
            current_error = error
            retryable = True

        except Exception as error:
            logger.exception(
                "Unexpected Gemini failure: attempt=%s/%s",
                attempt,
                max_attempts,
            )

            raise GeminiRequestError(
                "Gemini request failed unexpectedly."
            ) from error

        last_error = current_error

        logger.warning(
            "Gemini request failed: attempt=%s/%s "
            "retryable=%s error_type=%s error=%s",
            attempt,
            max_attempts,
            retryable,
            type(current_error).__name__,
            current_error,
        )

        if not retryable:
            logger.error(
                "Gemini request stopped after "
                "a non-retryable failure."
            )

            raise GeminiRequestError(
                "Gemini request failed with "
                "a non-retryable API error."
            ) from current_error

        if attempt < max_attempts:
            retry_delay_seconds = 2 ** (attempt - 1)

            logger.info(
                "Retrying Gemini request in %s seconds.",
                retry_delay_seconds,
            )

            time.sleep(retry_delay_seconds)

    logger.error(
        "Gemini request failed after %s total attempts.",
        max_attempts,
    )

    raise GeminiRequestError(
        f"Gemini request failed after "
        f"{max_attempts} total attempts."
    ) from last_error