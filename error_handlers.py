from fastapi import Request
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from logger import logger


async def http_error_handler(
    request: Request,
    error: HTTPException,
) -> JSONResponse:
    error_type = (
        "authentication_error"
        if error.status_code == 401
        else "http_error"
    )

    logger.warning(
        "HTTP request rejected: status=%s path=%s",
        error.status_code,
        request.url.path,
    )

    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "type": error_type,
                "message": str(error.detail),
            }
        },
    )


async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    reasons = [
        {
            "field": ".".join(str(part) for part in item["loc"]),
            "message": item["msg"],
            "type": item["type"],
        }
        for item in error.errors()
    ]

    logger.warning(
        "Request validation failed: path=%s reasons=%s",
        request.url.path,
        reasons,
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "validation_error",
                "message": "Request validation failed.",
                "reasons": reasons,
            }
        },
    )


async def rate_limit_error_handler(
    request: Request,
    error: RateLimitExceeded,
) -> JSONResponse:
    client = request.client.host if request.client else "unknown"

    logger.warning(
        "Rate limit exceeded: path=%s client=%s",
        request.url.path,
        client,
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "type": "rate_limit_exceeded",
                "message": "Rate limit exceeded. Try again later.",
            }
        },
    )