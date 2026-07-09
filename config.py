from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CV Optimizer & Interview Prep Assistant"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    backend_api_key: str = Field(validation_alias="BACKEND_API_KEY")
    rate_limit: str = Field(
        default="10/minute",
        validation_alias="RATE_LIMIT",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()