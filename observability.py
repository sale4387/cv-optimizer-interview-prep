from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import wraps
from time import perf_counter
from typing import Any, ParamSpec, TypeVar

from logger import logger


P = ParamSpec("P")
R = TypeVar("R")

SAFE_CONTEXT_KEYS = (
    "application_id",
    "company_key",
    "profile_id",
    "job_title",
)


def elapsed_ms(
    started_at: float,
) -> float:
    return round(
        (perf_counter() - started_at) * 1000,
        2,
    )


def _safe_text(
    value: Any,
    *,
    limit: int = 300,
) -> str:
    text = str(value).replace(
        "\n",
        " ",
    ).replace(
        "\r",
        " ",
    )

    return text[:limit]


def _read_value(
    source: Any,
    key: str,
) -> Any:
    if source is None:
        return None

    if isinstance(source, Mapping):
        return source.get(key)

    return getattr(
        source,
        key,
        None,
    )


def collect_safe_context(
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    result: Any = None,
) -> dict[str, str]:
    sources: list[Any] = [
        result,
        kwargs,
        *args[:2],
    ]

    context: dict[str, str] = {}

    for key in SAFE_CONTEXT_KEYS:
        for source in sources:
            value = _read_value(
                source,
                key,
            )

            if value not in {
                None,
                "",
            }:
                context[key] = (
                    _safe_text(
                        value,
                        limit=200,
                    )
                )
                break

    return context


def log_metric(
    *,
    event: str,
    status: str,
    duration_ms: float | None = None,
    attempt: int | None = None,
    max_attempts: int | None = None,
    error: BaseException | None = None,
    validation_reasons: Any = None,
    **context: Any,
) -> None:
    fields: dict[str, Any] = {
        "event": event,
        "status": status,
    }

    if duration_ms is not None:
        fields["duration_ms"] = round(
            duration_ms,
            2,
        )

    if attempt is not None:
        fields["attempt"] = attempt

    if max_attempts is not None:
        fields["max_attempts"] = (
            max_attempts
        )

    for key in SAFE_CONTEXT_KEYS:
        value = context.get(key)

        if value not in {
            None,
            "",
        }:
            fields[key] = _safe_text(
                value,
                limit=200,
            )

    operation = context.get(
        "operation"
    )

    if operation:
        fields["operation"] = _safe_text(
            operation,
            limit=250,
        )

    model = context.get("model")

    if model:
        fields["model"] = _safe_text(
            model,
            limit=100,
        )

    if error is not None:
        fields["error_type"] = (
            type(error).__name__
        )
        fields["error_message"] = (
            _safe_text(error)
        )

    if validation_reasons:
        if isinstance(
            validation_reasons,
            (list, tuple),
        ):
            reason_text = " | ".join(
                _safe_text(
                    reason,
                    limit=200,
                )
                for reason
                in validation_reasons[:10]
            )
        else:
            reason_text = _safe_text(
                validation_reasons,
                limit=500,
            )

        fields[
            "validation_failure_reason"
        ] = reason_text

    message = "metric " + " ".join(
        f"{key}={value!r}"
        for key, value
        in fields.items()
    )

    if status in {
        "failed",
        "error",
    }:
        logger.error(message)

    elif status in {
        "retry",
        "warning",
    }:
        logger.warning(message)

    else:
        logger.info(message)


def observe_function(
    event: str,
    *,
    static_context: (
        Mapping[str, Any] | None
    ) = None,
) -> Callable[
    [Callable[P, R]],
    Callable[P, R],
]:
    def decorator(
        function: Callable[P, R],
    ) -> Callable[P, R]:
        @wraps(function)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            started_at = perf_counter()

            context = collect_safe_context(
                args,
                kwargs,
            )

            if static_context:
                context.update(
                    {
                        key: value
                        for key, value
                        in static_context.items()
                        if value not in {
                            None,
                            "",
                        }
                    }
                )

            try:
                result = function(
                    *args,
                    **kwargs,
                )

            except Exception as error:
                reasons = getattr(
                    error,
                    "reasons",
                    None,
                )

                log_metric(
                    event=event,
                    status="failed",
                    duration_ms=elapsed_ms(
                        started_at
                    ),
                    error=error,
                    validation_reasons=(
                        reasons
                    ),
                    **context,
                )
                raise

            result_context = (
                collect_safe_context(
                    args,
                    kwargs,
                    result,
                )
            )
            context.update(
                result_context
            )

            log_metric(
                event=event,
                status="success",
                duration_ms=elapsed_ms(
                    started_at
                ),
                **context,
            )

            return result

        return wrapper

    return decorator
