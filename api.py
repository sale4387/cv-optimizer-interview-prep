from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import APP_NAME, APP_VERSION
from logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Application startup: %s v%s", APP_NAME, APP_VERSION)
    yield
    logger.info("Application shutdown: %s", APP_NAME)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, str]:
    logger.info("Root endpoint requested")

    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }