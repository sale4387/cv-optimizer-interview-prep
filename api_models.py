import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIRequestModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class CVOptimizationRequest(APIRequestModel):
    profile_id: str = Field(min_length=1, max_length=50)
    job_ad_text: str = Field(min_length=100, max_length=50_000)
    company_name: str = Field(min_length=4, max_length=200)

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        match = re.fullmatch(r"(.+?)\s*-\s*([A-Za-z]{2})", value)

        if match is None:
            raise ValueError(
                "Company name must use the format: Company Name - ISO2."
            )

        company, country_code = match.groups()

        return f"{company.strip()} - {country_code.upper()}"