from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from api_models import CVOptimizationRequest
from security import verify_api_key
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from error_handlers import (
    http_error_handler,
    rate_limit_error_handler,
    validation_error_handler,
)

from slowapi.errors import RateLimitExceeded
from rate_limit import limiter
from config import settings
from logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Application startup: %s v%s", settings.app_name, settings.app_version)
    yield
    logger.info("Application shutdown: %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(
    StarletteHTTPException,
    http_error_handler,
)
app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)
app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_error_handler,
)

@app.get("/")
def root() -> dict[str, str]:
    logger.info("Root endpoint requested")

    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
@app.post(
    "/optimize",
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(settings.rate_limit)
def optimize_cv(
    request: Request,
    payload: CVOptimizationRequest,
) -> dict[str, str]:
    logger.info(
        "Optimize endpoint requested for profile: %s",
        payload.profile_id,
    )

    return {
        "status": "accepted",
        "profile_id": payload.profile_id,
        "company_name": payload.company_name,
    }
def optimize_cv(request: CVOptimizationRequest) -> dict[str, str]:
    logger.info(
        "Optimize endpoint requested for profile: %s",
        request.profile_id,
    )

    return {
        "status": "accepted",
        "profile_id": request.profile_id,
        "company_name": request.company_name,
    }