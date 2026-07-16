from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


ResearchStatus = Literal[
    "complete",
    "limited",
]

ConfidenceLevel = Literal[
    "high",
    "medium",
    "low",
]

ProductType = Literal[
    "product",
    "service",
    "platform",
    "solution",
    "unknown",
]

RecentDevelopmentType = Literal[
    "news",
    "acquisition",
    "merger",
    "funding",
    "product",
    "partnership",
    "leadership",
    "financial",
    "other",
]

EmployeeSentimentSignal = Literal[
    "positive",
    "mixed",
    "negative",
    "insufficient_public_data",
]

SourceType = Literal[
    "official",
    "news",
    "financial",
    "review",
    "other",
]

ShortText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=2,
        max_length=500,
    ),
]

MediumText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=5,
        max_length=1500,
    ),
]

LongText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=10,
        max_length=3000,
    ),
]

CountryCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^[A-Z]{2}$",
    ),
]


class StrictCompanyResearchModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class IndustryInfo(StrictCompanyResearchModel):
    primary_industry: ShortText

    secondary_industries: list[
        ShortText
    ] = Field(
        default_factory=list,
        max_length=10,
    )

    business_model: MediumText


class ProductOrService(
    StrictCompanyResearchModel
):
    name: ShortText
    type: ProductType
    description: MediumText
    why_it_matters_for_interview: MediumText


class KnownPublicCustomer(
    StrictCompanyResearchModel
):
    name: ShortText
    context: MediumText


class CustomersAndMarket(
    StrictCompanyResearchModel
):
    known_public_customers: list[
        KnownPublicCustomer
    ] = Field(default_factory=list)

    customer_types: list[
        ShortText
    ] = Field(default_factory=list)

    target_markets: list[
        ShortText
    ] = Field(default_factory=list)

    limitations: MediumText | None = None

    @model_validator(mode="after")
    def validate_customer_signal(
        self,
    ) -> "CustomersAndMarket":
        if (
            not self.known_public_customers
            and not self.customer_types
            and not self.limitations
        ):
            raise ValueError(
                "Customer data requires known public customers, "
                "customer types or a limitation note."
            )

        return self


class Competitor(StrictCompanyResearchModel):
    name: ShortText
    reason: MediumText
    comparison_note: MediumText | None = None


class RecentDevelopment(
    StrictCompanyResearchModel
):
    date: ShortText
    type: RecentDevelopmentType
    title: ShortText
    summary: MediumText
    interview_relevance: MediumText


class PublicCompanyInformation(
    StrictCompanyResearchModel
):
    is_public_company: bool
    ticker: ShortText | None = None
    exchange: ShortText | None = None
    summary: MediumText | None = None
    limitations: MediumText | None = None

    @model_validator(mode="after")
    def validate_public_company_fields(
        self,
    ) -> "PublicCompanyInformation":
        if not self.is_public_company and (
            self.ticker or self.exchange
        ):
            raise ValueError(
                "Ticker and exchange are allowed only "
                "for public companies."
            )

        if (
            self.is_public_company
            and not self.summary
            and not self.limitations
        ):
            raise ValueError(
                "Public company information requires "
                "a summary or limitation note."
            )

        return self


class EmployeeSentiment(
    StrictCompanyResearchModel
):
    signal: EmployeeSentimentSignal
    summary: MediumText
    positive_themes: list[
        ShortText
    ] = Field(default_factory=list)

    negative_themes: list[
        ShortText
    ] = Field(default_factory=list)

    interview_caution: MediumText
    limitations: MediumText | None = None

    @model_validator(mode="after")
    def validate_sentiment_limitations(
        self,
    ) -> "EmployeeSentiment":
        if (
            self.signal == "insufficient_public_data"
            and not self.limitations
        ):
            raise ValueError(
                "Insufficient employee sentiment data "
                "requires a limitation note."
            )

        return self


class TalkingPoint(
    StrictCompanyResearchModel
):
    topic: ShortText
    why_it_matters: MediumText
    how_to_use: MediumText


class InterviewRisk(
    StrictCompanyResearchModel
):
    risk: MediumText
    preparation_note: MediumText


class InterviewIntelligence(
    StrictCompanyResearchModel
):
    talking_points: list[
        TalkingPoint
    ] = Field(min_length=1, max_length=10)

    risks_to_prepare_for: list[
        InterviewRisk
    ] = Field(default_factory=list, max_length=10)

    @model_validator(mode="before")
    @classmethod
    def remove_legacy_questions_to_ask(
        cls,
        value: object,
    ) -> object:
        """Accept old cached reports but remove duplicated questions."""
        if isinstance(value, dict):
            cleaned_value = dict(value)
            cleaned_value.pop(
                "questions_to_ask",
                None,
            )
            return cleaned_value

        return value


class ResearchSource(
    StrictCompanyResearchModel
):
    title: ShortText
    url: ShortText
    publisher: ShortText
    source_type: SourceType

    supports: list[
        ShortText
    ] = Field(min_length=1, max_length=20)

    accessed_at: ShortText


class CompanyResearchReport(
    StrictCompanyResearchModel
):
    company_key: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=4,
            max_length=200,
            pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*-[a-z]{2}$",
        ),
    ]

    display_name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=4,
            max_length=200,
        ),
    ]

    country_code: CountryCode
    research_status: ResearchStatus
    confidence_level: ConfidenceLevel
    short_description: LongText
    industry: IndustryInfo

    products_and_services: list[
        ProductOrService
    ] = Field(min_length=1, max_length=20)

    customers_and_market: CustomersAndMarket

    competitors: list[
        Competitor
    ] = Field(min_length=1, max_length=20)

    recent_developments: list[
        RecentDevelopment
    ] = Field(default_factory=list, max_length=15)

    public_company_information: PublicCompanyInformation

    employee_sentiment: EmployeeSentiment

    interview_intelligence: InterviewIntelligence

    sources: list[
        ResearchSource
    ] = Field(default_factory=list, max_length=30)

    limitations: list[
        MediumText
    ] = Field(default_factory=list, max_length=20)

    generated_at: datetime
    valid_until: datetime

    @model_validator(mode="after")
    def validate_status_and_sources(
        self,
    ) -> "CompanyResearchReport":
        if self.valid_until <= self.generated_at:
            raise ValueError(
                "valid_until must be after generated_at."
            )

        if (
            self.research_status == "complete"
            and not self.sources
        ):
            raise ValueError(
                "Complete company research requires "
                "at least one source."
            )

        if (
            self.research_status == "limited"
            and not self.limitations
        ):
            raise ValueError(
                "Limited company research requires "
                "at least one limitation."
            )

        return self
