import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config import settings
from logger import logger


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def verify_api_key(
    provided_api_key: str | None = Security(api_key_header),
) -> str:
    if provided_api_key is None:
        logger.warning("Request rejected: API key is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing.",
        )

    if not secrets.compare_digest(
        provided_api_key,
        settings.backend_api_key,
    ):
        logger.warning("Request rejected: API key is invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is invalid.",
        )

    return provided_api_key