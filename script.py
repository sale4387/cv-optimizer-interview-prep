from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from typing import Callable
from unittest.mock import patch
from uuid import uuid4

from google.api_core.exceptions import DeadlineExceeded
from pydantic import ValidationError

import firebase as storage


RUN_ID = uuid4().hex[:8]

COMPANY_LABEL = f"Firebase Storage Test {RUN_ID} - NL"
COMPANY_KEY = storage.normalize_company_key(COMPANY_LABEL)

MALFORMED_COMPANY_KEY = (
    f"malformed-storage-test-{RUN_ID}-nl"
)
NONEXISTENT_COMPANY_KEY = (
    f"nonexistent-storage-test-{RUN_ID}-nl"
)

CREATED_APPLICATION_IDS: list[str] = []


class LogCaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@contextmanager
def capture_storage_logs(
    level: int = logging.DEBUG,
):
    handler = LogCaptureHandler()
    previous_level = storage.logger.level

    storage.logger.setLevel(level)
    storage.logger.addHandler(handler)

    try:
        yield handler.records
    finally:
        storage.logger.removeHandler(handler)
        storage.logger.setLevel(previous_level)


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
    ), (
        f"Expected log message containing "
        f"'{expected_text}' was not found."
    )


def application_payload() -> dict:
    return {
        "profile_id": "sale",
        "company_key": COMPANY_KEY,
        "job_title": "Firebase Test Role",
        "job_ad_hash": f"hash-{RUN_ID}",
        "status": "draft",
        "fit_assessment": {
            "score": 80,
        },
        "tailored_cv": None,
        "gap_analysis": {
            "gaps": [],
        },
        "interview_prep": None,
        "base_cv_version": "1.0",
        "schema_version": "1.0",
        "prompt_version": "1.0",
        "model_version": "test-model",
    }


def test_company_save_and_read() -> None:
    company_key = storage.save_company(
        company_label=COMPANY_LABEL,
        company_research={
            "summary": "Initial Firebase test record",
        },
        schema_version="1.0",
        prompt_version="1.0",
        model_version="test-model",
    )

    assert company_key == COMPANY_KEY

    loaded_record = storage.get_company_by_key(
        company_key
    )

    assert loaded_record is not None
    assert loaded_record["company_key"] == COMPANY_KEY
    assert (
        loaded_record["company_research"]["summary"]
        == "Initial Firebase test record"
    )


def test_application_save_and_read() -> None:
    first_application_id = storage.save_application(
        application_payload()
    )

    second_application_id = storage.save_application(
        application_payload()
    )

    CREATED_APPLICATION_IDS.extend(
        [
            first_application_id,
            second_application_id,
        ]
    )

    assert first_application_id
    assert second_application_id
    assert (
        first_application_id
        != second_application_id
    )

    loaded_record = storage.get_application(
        first_application_id
    )

    assert loaded_record is not None
    assert (
        loaded_record["application_id"]
        == first_application_id
    )
    assert loaded_record["company_key"] == COMPANY_KEY


def test_invalid_input_rejected() -> None:
    try:
        storage.save_application(
            {
                "profile_id": "sale",
            }
        )
    except ValidationError:
        return

    raise AssertionError(
        "Application missing mandatory fields "
        "was not rejected."
    )


def test_missing_credentials_logged() -> None:
    storage.get_firestore_client.cache_clear()

    try:
        with patch.object(
            storage.settings,
            "firebase_credentials_path",
            "secrets/credentials-do-not-exist.json",
        ):
            with capture_storage_logs(
                logging.ERROR
            ) as records:
                try:
                    storage.get_firestore_client()
                except FileNotFoundError:
                    pass
                else:
                    raise AssertionError(
                        "Missing credentials did not "
                        "raise FileNotFoundError."
                    )

            assert_log_contains(
                records,
                "Firebase credentials were not found",
            )
    finally:
        storage.get_firestore_client.cache_clear()


def test_retry_stops_after_three_attempts() -> None:
    attempts = 0

    def failing_operation() -> None:
        nonlocal attempts
        attempts += 1

        raise DeadlineExceeded(
            "Forced timeout for storage test"
        )

    with patch.object(
        storage.time,
        "sleep",
        return_value=None,
    ):
        with capture_storage_logs(
            logging.WARNING
        ) as records:
            try:
                storage._run_with_retry(
                    operation_name="forced timeout test",
                    operation=failing_operation,
                )
            except DeadlineExceeded:
                pass
            else:
                raise AssertionError(
                    "Retryable failure did not propagate "
                    "after maximum attempts."
                )

    assert attempts == 3, (
        f"Expected 3 attempts, got {attempts}."
    )

    assert_log_contains(
        records,
        "attempt=3/3",
    )

    assert_log_contains(
        records,
        "failed after maximum attempts",
    )


def test_nonexistent_document_returns_none() -> None:
    result = storage.get_company_by_key(
        NONEXISTENT_COMPANY_KEY
    )

    assert result is None


def test_existing_company_is_reused() -> None:
    original_record = storage.get_company_by_key(
        COMPANY_KEY
    )

    assert original_record is not None

    original_created_at = original_record[
        "created_at"
    ]

    reused_key = storage.save_company(
        company_label=COMPANY_LABEL,
        company_research={
            "summary": "Updated existing company",
        },
        schema_version="1.0",
        prompt_version="1.1",
        model_version="test-model",
    )

    updated_record = storage.get_company_by_key(
        COMPANY_KEY
    )

    assert reused_key == COMPANY_KEY
    assert updated_record is not None

    assert (
        updated_record["created_at"]
        == original_created_at
    )

    assert (
        updated_record["company_research"]["summary"]
        == "Updated existing company"
    )


def test_malformed_stored_data_rejected() -> None:
    client = storage.get_firestore_client()

    document = (
        client.collection(
            storage.COMPANIES_COLLECTION
        )
        .document(MALFORMED_COMPANY_KEY)
    )

    document.set(
        {
            "company_key": MALFORMED_COMPANY_KEY,
            "display_name": "Malformed Company - NL",
        }
    )

    try:
        storage.get_company_by_key(
            MALFORMED_COMPANY_KEY
        )
    except ValidationError:
        return

    raise AssertionError(
        "Malformed stored company data "
        "was not rejected."
    )


def cleanup_test_records() -> None:
    storage.get_firestore_client.cache_clear()

    try:
        client = storage.get_firestore_client()

        for application_id in CREATED_APPLICATION_IDS:
            (
                client.collection(
                    storage.APPLICATIONS_COLLECTION
                )
                .document(application_id)
                .delete()
            )

        for company_key in {
            COMPANY_KEY,
            MALFORMED_COMPANY_KEY,
        }:
            (
                client.collection(
                    storage.COMPANIES_COLLECTION
                )
                .document(company_key)
                .delete()
            )

    except Exception as error:
        print(
            "[WARNING] Test cleanup failed: "
            f"{type(error).__name__}: {error}"
        )


TESTS: list[
    tuple[str, Callable[[], None]]
] = [
    (
        "Company record saved and read",
        test_company_save_and_read,
    ),
    (
        "Application saved with unique ID and read",
        test_application_save_and_read,
    ),
    (
        "Invalid input rejected",
        test_invalid_input_rejected,
    ),
    (
        "Missing credentials handled and logged",
        test_missing_credentials_logged,
    ),
    (
        "Retryable failure stops after 3 attempts",
        test_retry_stops_after_three_attempts,
    ),
    (
        "Nonexistent document returns None",
        test_nonexistent_document_returns_none,
    ),
    (
        "Existing company record reused",
        test_existing_company_is_reused,
    ),
    (
        "Malformed stored data rejected",
        test_malformed_stored_data_rejected,
    ),
]


def main() -> int:
    passed = 0
    failed = 0

    original_handlers = list(
        storage.logger.handlers
    )
    original_propagate = storage.logger.propagate
    original_level = storage.logger.level

    storage.logger.handlers = []
    storage.logger.propagate = False
    storage.logger.setLevel(logging.DEBUG)

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
        cleanup_test_records()

        storage.logger.handlers = original_handlers
        storage.logger.propagate = (
            original_propagate
        )
        storage.logger.setLevel(original_level)

    print()
    print(
        f"Result: {passed} passed, {failed} failed"
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())