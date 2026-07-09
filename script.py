from __future__ import annotations

import logging
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Callable
from unittest.mock import Mock, patch

from google.genai import errors

import ai.ai_client as ai_client
from ai.prompts import SIMPLE_TEST_PROMPT


class LogCaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@contextmanager
def capture_logs():
    handler = LogCaptureHandler()
    ai_client.logger.addHandler(handler)

    try:
        yield handler.records
    finally:
        ai_client.logger.removeHandler(handler)


def assert_log_contains(
    records: list[logging.LogRecord],
    expected_text: str,
) -> None:
    messages = [
        record.getMessage()
        for record in records
    ]

    assert any(
        expected_text in message
        for message in messages
    ), f"Missing expected log: {expected_text}"


def create_mock_client(
    *,
    response_text: str | None = None,
    error: Exception | None = None,
) -> Mock:
    client = Mock()

    if error is not None:
        client.models.generate_content.side_effect = error
    else:
        client.models.generate_content.return_value = (
            SimpleNamespace(text=response_text)
        )

    return client


def test_live_gemini_request() -> None:
    result = ai_client.send_gemini_request(
        SIMPLE_TEST_PROMPT
    )

    assert isinstance(result, str)
    assert result.strip()
    assert "Gemini connection successful" in result


def test_timeout_retries_and_logs() -> None:
    client = create_mock_client(
        error=TimeoutError("Forced timeout")
    )

    with (
        patch.object(
            ai_client,
            "get_gemini_client",
            return_value=client,
        ),
        patch.object(
            ai_client.settings,
            "gemini_max_attempts",
            3,
        ),
        patch.object(
            ai_client.time,
            "sleep",
            return_value=None,
        ),
        capture_logs() as records,
    ):
        try:
            ai_client.send_gemini_request(
                "Timeout test"
            )
        except ai_client.GeminiRequestError:
            pass
        else:
            raise AssertionError(
                "Timeout did not produce a controlled error."
            )

    assert client.models.generate_content.call_count == 3
    assert_log_contains(records, "attempt=3/3")


def test_api_failure_is_logged() -> None:
    api_error = errors.ClientError(
        400,
        {
            "error": {
                "code": 400,
                "status": "INVALID_ARGUMENT",
                "message": "Forced API failure",
            }
        },
    )

    client = create_mock_client(error=api_error)

    with (
        patch.object(
            ai_client,
            "get_gemini_client",
            return_value=client,
        ),
        patch.object(
            ai_client.time,
            "sleep",
            return_value=None,
        ),
        capture_logs() as records,
    ):
        try:
            ai_client.send_gemini_request(
                "API failure test"
            )
        except ai_client.GeminiRequestError:
            pass
        else:
            raise AssertionError(
                "API failure was not controlled."
            )

    assert client.models.generate_content.call_count == 1
    assert_log_contains(
        records,
        "non-retryable failure",
    )


def test_empty_response_is_rejected() -> None:
    client = create_mock_client(response_text="   ")

    with (
        patch.object(
            ai_client,
            "get_gemini_client",
            return_value=client,
        ),
        patch.object(
            ai_client.settings,
            "gemini_max_attempts",
            3,
        ),
        patch.object(
            ai_client.time,
            "sleep",
            return_value=None,
        ),
        capture_logs() as records,
    ):
        try:
            ai_client.send_gemini_request(
                "Empty response test"
            )
        except ai_client.GeminiRequestError:
            pass
        else:
            raise AssertionError(
                "Empty response was not rejected."
            )

    assert client.models.generate_content.call_count == 3
    assert_log_contains(
        records,
        "EmptyGeminiResponseError",
    )


def test_maximum_attempts_are_enforced() -> None:
    api_error = errors.ServerError(
        503,
        {
            "error": {
                "code": 503,
                "status": "UNAVAILABLE",
                "message": "Forced retryable failure",
            }
        },
    )

    client = create_mock_client(error=api_error)

    with (
        patch.object(
            ai_client,
            "get_gemini_client",
            return_value=client,
        ),
        patch.object(
            ai_client.settings,
            "gemini_max_attempts",
            3,
        ),
        patch.object(
            ai_client.time,
            "sleep",
            return_value=None,
        ),
        capture_logs() as records,
    ):
        try:
            ai_client.send_gemini_request(
                "Maximum attempts test"
            )
        except ai_client.GeminiRequestError:
            pass
        else:
            raise AssertionError(
                "Retryable failure did not stop."
            )

    assert client.models.generate_content.call_count == 3

    assert_log_contains(
        records,
        "failed after 3 total attempts",
    )


def test_api_key_is_not_tracked() -> None:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )

    tracked_files = result.stdout.splitlines()

    assert ".env" not in tracked_files

    api_key = ai_client.settings.gemini_api_key

    for filename in tracked_files:
        path = Path(filename)

        if not path.is_file():
            continue

        try:
            content = path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            continue

        assert api_key not in content, (
            f"Gemini API key found in tracked file: "
            f"{filename}"
        )


TESTS: list[tuple[str, Callable[[], None]]] = [
    (
        "Valid Gemini request returns text",
        test_live_gemini_request,
    ),
    (
        "Timeout retries and is logged",
        test_timeout_retries_and_logs,
    ),
    (
        "API failure is controlled and logged",
        test_api_failure_is_logged,
    ),
    (
        "Empty response is rejected",
        test_empty_response_is_rejected,
    ),
    (
        "Processing stops after 3 attempts",
        test_maximum_attempts_are_enforced,
    ),
    (
        "Gemini API key is not tracked",
        test_api_key_is_not_tracked,
    ),
]


def main() -> int:
    passed = 0
    failed = 0

    original_handlers = list(
        ai_client.logger.handlers
    )
    original_propagate = (
        ai_client.logger.propagate
    )

    ai_client.logger.handlers = []
    ai_client.logger.propagate = False

    try:
        for test_name, test_function in TESTS:
            try:
                test_function()
            except Exception as error:
                failed += 1

                print(
                    f"[FAIL] {test_name} — "
                    f"{type(error).__name__}: {error}"
                )
            else:
                passed += 1
                print(f"[PASS] {test_name}")
    finally:
        ai_client.logger.handlers = (
            original_handlers
        )
        ai_client.logger.propagate = (
            original_propagate
        )

    print()
    print(
        f"Result: {passed} passed, {failed} failed"
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())