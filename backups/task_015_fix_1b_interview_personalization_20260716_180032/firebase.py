import re
import time
import unicodedata
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Literal, TypeVar
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.exceptions import (
    Aborted,
    DeadlineExceeded,
    InternalServerError,
    ServiceUnavailable,
    TooManyRequests,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from config import settings
from logger import logger


PROJECT_ROOT = Path(__file__).resolve().parent

COMPANIES_COLLECTION = "companies"
APPLICATIONS_COLLECTION = "applications"

FIRESTORE_TIMEOUT_SECONDS = 10.0
FIRESTORE_MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.0

AMSTERDAM_TIMEZONE = ZoneInfo("Europe/Amsterdam")

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=BaseModel)

RETRYABLE_FIRESTORE_ERRORS = (
    Aborted,
    DeadlineExceeded,
    InternalServerError,
    ServiceUnavailable,
    TooManyRequests,
)


class StorageModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class CompanyRecordInput(StorageModel):
    display_name: str = Field(min_length=4, max_length=200)
    company_research: dict[str, Any] = Field(min_length=1)
    schema_version: str = Field(min_length=1, max_length=50)
    prompt_version: str = Field(min_length=1, max_length=50)
    model_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class CompanyStoredRecord(CompanyRecordInput):
    company_key: str
    created_at: datetime
    updated_at: datetime


class ApplicationRecordInput(StorageModel):
    profile_id: str = Field(min_length=1, max_length=50)
    company_key: str = Field(min_length=4, max_length=200)
    job_title: str = Field(min_length=1, max_length=200)
    job_ad_hash: str = Field(min_length=8, max_length=200)

    status: Literal["draft", "accepted"] = "draft"

    fit_assessment: dict[str, Any] = Field(min_length=1)
    tailored_cv: dict[str, Any] | None = None
    gap_analysis: dict[str, Any] = Field(min_length=1)
    candidate: dict[str, Any] | None = None
    company_research: dict[str, Any] | None = None
    interview_prep: dict[str, Any] | None = None
    workflow_status: dict[str, Any] | None = None

    base_cv_version: str = Field(min_length=1, max_length=50)
    schema_version: str = Field(min_length=1, max_length=50)
    prompt_version: str = Field(min_length=1, max_length=50)
    model_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    @field_validator("company_key")
    @classmethod
    def validate_company_key(cls, value: str) -> str:
        if not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*-[a-z]{2}",
            value,
        ):
            raise ValueError(
                "Company key must be normalized, for example: bird-nl."
            )

        return value


class ApplicationStoredRecord(ApplicationRecordInput):
    application_id: str
    created_at: datetime
    updated_at: datetime
    accepted_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_interview_prep(
        cls,
        data: Any,
    ) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        canonical = normalized.get(
            "interview_prep"
        )

        if canonical is None:
            canonical = (
                normalized.get(
                    "application_interview_prep"
                )
                or normalized.get(
                    "interview_preparation"
                )
            )

        if canonical is not None:
            normalized[
                "interview_prep"
            ] = canonical

        normalized.pop(
            "interview_preparation",
            None,
        )
        normalized.pop(
            "application_interview_prep",
            None,
        )

        return normalized


def _validate_record(
    model: type[ModelT],
    data: dict[str, Any],
    context: str,
) -> ModelT:
    try:
        return model.model_validate(data)

    except ValidationError:
        logger.exception(
            "Firestore record validation failed: %s",
            context,
        )
        raise


def _run_with_retry(
    operation_name: str,
    operation: Callable[[], T],
) -> T:
    from time import perf_counter

    from observability import (
        elapsed_ms,
        log_metric,
    )

    overall_started_at = perf_counter()

    for attempt in range(
        1,
        FIRESTORE_MAX_ATTEMPTS + 1,
    ):
        attempt_started_at = (
            perf_counter()
        )

        try:
            result = operation()

        except (
            RETRYABLE_FIRESTORE_ERRORS
        ) as error:
            final_attempt = (
                attempt
                == FIRESTORE_MAX_ATTEMPTS
            )

            log_metric(
                event="firestore_operation",
                status=(
                    "failed"
                    if final_attempt
                    else "retry"
                ),
                duration_ms=elapsed_ms(
                    attempt_started_at
                ),
                attempt=attempt,
                max_attempts=(
                    FIRESTORE_MAX_ATTEMPTS
                ),
                operation=operation_name,
                error=error,
            )

            logger.warning(
                "Firestore operation failed: operation=%s "
                "attempt=%s/%s error=%s",
                operation_name,
                attempt,
                FIRESTORE_MAX_ATTEMPTS,
                type(error).__name__,
            )

            if final_attempt:
                raise

            time.sleep(
                RETRY_DELAY_SECONDS
                * attempt
            )

        except Exception as error:
            log_metric(
                event="firestore_operation",
                status="failed",
                duration_ms=elapsed_ms(
                    attempt_started_at
                ),
                attempt=attempt,
                max_attempts=(
                    FIRESTORE_MAX_ATTEMPTS
                ),
                operation=operation_name,
                error=error,
            )

            logger.exception(
                "Non-retryable Firestore failure: %s",
                operation_name,
            )
            raise

        else:
            log_metric(
                event="firestore_operation",
                status="success",
                duration_ms=elapsed_ms(
                    overall_started_at
                ),
                attempt=attempt,
                max_attempts=(
                    FIRESTORE_MAX_ATTEMPTS
                ),
                operation=operation_name,
            )

            return result

    raise RuntimeError(
        f"Firestore operation ended unexpectedly: {operation_name}"
    )


@lru_cache(maxsize=1)
def get_firestore_client():
    credential_path = Path(settings.firebase_credentials_path)

    if not credential_path.is_absolute():
        credential_path = PROJECT_ROOT / credential_path

    if not credential_path.exists():
        message = (
            f"Firebase credentials were not found: {credential_path}"
        )
        logger.error(message)
        raise FileNotFoundError(message)

    try:
        firebase_app = firebase_admin.get_app()

    except ValueError:
        credential = credentials.Certificate(str(credential_path))
        firebase_app = firebase_admin.initialize_app(credential)

        logger.info("Firebase Admin SDK initialized")

    client = firestore.client(app=firebase_app)

    logger.info("Firestore client initialized")

    return client


def normalize_company_key(company_label: str) -> str:
    match = re.fullmatch(
        r"\s*(.+?)\s*-\s*([A-Za-z]{2})\s*",
        company_label,
    )

    if match is None:
        raise ValueError(
            "Company label must use the format: Company Name - ISO2."
        )

    company_name, country_code = match.groups()

    ascii_name = (
        unicodedata.normalize("NFKD", company_name)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )

    normalized_name = re.sub(
        r"[^a-z0-9]+",
        "-",
        ascii_name,
    ).strip("-")

    if not normalized_name:
        raise ValueError("Company name cannot be normalized.")

    return f"{normalized_name}-{country_code.lower()}"


def _validate_document_id(document_id: str) -> str:
    normalized_id = document_id.strip()

    if not normalized_id or "/" in normalized_id:
        raise ValueError("Invalid Firestore document ID.")

    return normalized_id


def save_company(
    company_label: str,
    company_research: dict[str, Any],
    schema_version: str,
    prompt_version: str,
    model_version: str | None = None,
) -> str:
    company_key = normalize_company_key(company_label)

    validated_input = _validate_record(
        CompanyRecordInput,
        {
            "display_name": company_label,
            "company_research": company_research,
            "schema_version": schema_version,
            "prompt_version": prompt_version,
            "model_version": model_version,
        },
        context=f"company input {company_key}",
    )

    client = get_firestore_client()

    document = (
        client.collection(COMPANIES_COLLECTION)
        .document(company_key)
    )

    existing_snapshot = _run_with_retry(
        operation_name=f"read company {company_key}",
        operation=lambda: document.get(
            retry=None,
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        ),
    )

    record: dict[str, Any] = {
        **validated_input.model_dump(mode="python"),
        "company_key": company_key,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    if not existing_snapshot.exists:
        record["created_at"] = firestore.SERVER_TIMESTAMP

    _run_with_retry(
        operation_name=f"save company {company_key}",
        operation=lambda: document.set(
            record,
            merge=True,
            retry=None,
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        ),
    )

    logger.info("Company record saved: %s", company_key)

    return company_key


def get_company_by_key(
    company_key: str,
) -> dict[str, Any] | None:
    company_key = _validate_document_id(company_key)

    client = get_firestore_client()

    document = (
        client.collection(COMPANIES_COLLECTION)
        .document(company_key)
    )

    snapshot = _run_with_retry(
        operation_name=f"read company {company_key}",
        operation=lambda: document.get(
            retry=None,
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        ),
    )

    if not snapshot.exists:
        logger.info("Company record not found: %s", company_key)
        return None

    data = snapshot.to_dict()

    if data is None:
        raise ValueError(
            f"Company record contains no data: {company_key}"
        )

    validated_record = _validate_record(
        CompanyStoredRecord,
        data,
        context=f"stored company {company_key}",
    )

    logger.info("Company record loaded: %s", company_key)

    return validated_record.model_dump(mode="python")


def get_company(
    company_label: str,
) -> dict[str, Any] | None:
    company_key = normalize_company_key(company_label)
    return get_company_by_key(company_key)


def save_application(
    application_data: dict[str, Any],
) -> str:
    validated_input = _validate_record(
        ApplicationRecordInput,
        application_data,
        context="application input",
    )

    client = get_firestore_client()

    application_reference = (
        client.collection(APPLICATIONS_COLLECTION)
        .document()
    )

    application_id = application_reference.id

    record: dict[str, Any] = {
        **validated_input.model_dump(mode="python"),
        "application_id": application_id,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "accepted_at": (
            firestore.SERVER_TIMESTAMP
            if validated_input.status == "accepted"
            else None
        ),
    }

    _run_with_retry(
        operation_name=f"save application {application_id}",
        operation=lambda: application_reference.set(
            record,
            retry=None,
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        ),
    )

    logger.info(
        "Application record saved: application_id=%s profile_id=%s",
        application_id,
        validated_input.profile_id,
    )

    return application_id


def get_application(
    application_id: str,
) -> dict[str, Any] | None:
    application_id = _validate_document_id(application_id)

    client = get_firestore_client()

    document = (
        client.collection(APPLICATIONS_COLLECTION)
        .document(application_id)
    )

    snapshot = _run_with_retry(
        operation_name=f"read application {application_id}",
        operation=lambda: document.get(
            retry=None,
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        ),
    )

    if not snapshot.exists:
        logger.info(
            "Application record not found: %s",
            application_id,
        )
        return None

    data = snapshot.to_dict()

    if data is None:
        raise ValueError(
            f"Application record contains no data: {application_id}"
        )

    validated_record = _validate_record(
        ApplicationStoredRecord,
        data,
        context=f"stored application {application_id}",
    )

    logger.info(
        "Application record loaded: %s",
        application_id,
    )

    return validated_record.model_dump(mode="python")


def format_timestamp_amsterdam(
    timestamp: datetime,
    date_format: str = "%Y-%m-%d %H:%M:%S %Z",
) -> str:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(
        AMSTERDAM_TIMEZONE
    ).strftime(date_format)

def list_applications(
    profile_id: str | None = None,
) -> list[dict[str, Any]]:
    client = get_firestore_client()

    snapshots = _run_with_retry(
        operation_name="list applications",
        operation=lambda: list(
            client.collection(
                APPLICATIONS_COLLECTION
            ).stream(
                retry=None,
                timeout=FIRESTORE_TIMEOUT_SECONDS,
            )
        ),
    )

    records: list[dict[str, Any]] = []

    for snapshot in snapshots:
        data = snapshot.to_dict()

        if data is None:
            logger.error(
                "Application record contains no data: %s",
                snapshot.id,
            )
            continue

        try:
            validated_record = _validate_record(
                ApplicationStoredRecord,
                data,
                context=(
                    f"stored application {snapshot.id}"
                ),
            )
        except ValidationError:
            logger.error(
                "Invalid application skipped while listing: %s",
                snapshot.id,
            )
            continue

        record = validated_record.model_dump(
            mode="python"
        )

        if (
            profile_id is not None
            and record["profile_id"] != profile_id
        ):
            continue

        records.append(record)

    records.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    logger.info(
        "Application records listed: count=%s profile_id=%s",
        len(records),
        profile_id,
    )

    return records
def update_application(
    application_id: str,
    application_updates: dict[str, Any],
) -> str:
    application_id = _validate_document_id(
        application_id
    )

    allowed_fields = set(
        ApplicationRecordInput
        .model_fields
    )

    unexpected_fields = (
        set(application_updates)
        - allowed_fields
    )

    if unexpected_fields:
        raise ValueError(
            "Unexpected application update fields: "
            + ", ".join(
                sorted(
                    unexpected_fields
                )
            )
        )

    existing_record = get_application(
        application_id
    )

    if existing_record is None:
        raise KeyError(
            f"Application does not exist: "
            f"{application_id}"
        )

    merged_input = {
        field_name: (
            application_updates[
                field_name
            ]
            if field_name
            in application_updates
            else existing_record[
                field_name
            ]
        )
        for field_name in allowed_fields
    }

    validated_input = _validate_record(
        ApplicationRecordInput,
        merged_input,
        context=(
            f"application update "
            f"{application_id}"
        ),
    )

    accepted_at: Any = None

    if (
        validated_input.status
        == "accepted"
    ):
        accepted_at = (
            existing_record.get(
                "accepted_at"
            )
            or firestore.SERVER_TIMESTAMP
        )

    record: dict[str, Any] = {
        **validated_input.model_dump(
            mode="python"
        ),
        "application_id": (
            application_id
        ),
        "created_at": (
            existing_record[
                "created_at"
            ]
        ),
        "updated_at": (
            firestore.SERVER_TIMESTAMP
        ),
        "accepted_at": accepted_at,
    }

    client = get_firestore_client()

    document = (
        client.collection(
            APPLICATIONS_COLLECTION
        )
        .document(application_id)
    )

    _run_with_retry(
        operation_name=(
            f"update application "
            f"{application_id}"
        ),
        operation=lambda: document.set(
            record,
            merge=False,
            retry=None,
            timeout=(
                FIRESTORE_TIMEOUT_SECONDS
            ),
        ),
    )

    logger.info(
        "Application record updated: "
        "application_id=%s status=%s",
        application_id,
        validated_input.status,
    )

    return application_id
def list_companies() -> list[dict[str, Any]]:
    client = get_firestore_client()

    snapshots = _run_with_retry(
        operation_name="list companies",
        operation=lambda: list(
            client.collection(
                COMPANIES_COLLECTION
            ).stream(
                retry=None,
                timeout=FIRESTORE_TIMEOUT_SECONDS,
            )
        ),
    )

    records: list[dict[str, Any]] = []

    for snapshot in snapshots:
        data = snapshot.to_dict()

        if data is None:
            logger.error(
                "Company record contains no data: %s",
                snapshot.id,
            )
            continue

        try:
            validated_record = _validate_record(
                CompanyStoredRecord,
                data,
                context=(
                    f"stored company {snapshot.id}"
                ),
            )
        except ValidationError:
            logger.error(
                "Invalid company skipped while listing: %s",
                snapshot.id,
            )
            continue

        records.append(
            validated_record.model_dump(
                mode="python"
            )
        )

    records.sort(
        key=lambda item: item["updated_at"],
        reverse=True,
    )

    logger.info(
        "Company records listed: count=%s",
        len(records),
    )

    return records
