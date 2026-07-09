from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CV Optimizer & Interview Prep Assistant"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    backend_api_key: str = Field(validation_alias="BACKEND_API_KEY")
    firebase_credentials_path: str = Field(
    validation_alias="FIREBASE_CREDENTIALS_PATH",
    )
    gemini_api_key: str = Field(
    validation_alias="GEMINI_API_KEY",
    )
    gemini_model: str = Field(
        default="gemini-3.5-flash",
        validation_alias="GEMINI_MODEL",
    )
    gemini_max_output_tokens: int = Field(
        default=8192,
        validation_alias="GEMINI_MAX_OUTPUT_TOKENS",
    )
    gemini_timeout_seconds: float = Field(
        default=60.0,
        validation_alias="GEMINI_TIMEOUT_SECONDS",
    )
    gemini_max_attempts: int = Field(
        default=3,
        validation_alias="GEMINI_MAX_ATTEMPTS",
    )
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