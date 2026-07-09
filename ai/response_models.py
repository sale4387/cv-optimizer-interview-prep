from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


FitLevel = Literal[
    "strong",
    "solid",
    "stretch",
    "poor",
]

ImpactLevel = Literal[
    "low",
    "medium",
    "high",
]


RelevantExperienceText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=10,
        max_length=500,
    ),
]

MissingRequirementText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=5,
        max_length=300,
    ),
]

SummaryText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=80,
        max_length=700,
    ),
]

ResponsibilityText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=20,
        max_length=400,
    ),
]

RequirementText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=5,
        max_length=500,
    ),
]

RecommendationText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=20,
        max_length=1000,
    ),
]

WarningText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=5,
        max_length=300,
    ),
]

SkillText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

ExperienceIdText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]


class StrictResponseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class FitAssessment(StrictResponseModel):
    level: FitLevel

    explanation: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=50,
            max_length=1000,
        ),
    ]

    relevant_experience: list[
        RelevantExperienceText
    ] = Field(
        min_length=1,
    )

    missing_requirements: list[
        MissingRequirementText
    ]


class ExperienceUpdate(StrictResponseModel):
    experience_id: ExperienceIdText

    suggested_job_title: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=200,
        ),
    ] | None = None

    responsibilities: list[
        ResponsibilityText
    ] = Field(
        min_length=1,
        max_length=6,
    )


class CVPatch(StrictResponseModel):
    professional_summary: SummaryText

    experience_updates: list[
        ExperienceUpdate
    ] = Field(
        min_length=1,
    )

    skills_to_highlight: list[
        SkillText
    ] = Field(
        min_length=1,
        max_length=30,
    )


class UnsupportedRequirement(
    StrictResponseModel
):
    requirement: RequirementText
    impact: ImpactLevel

    preparation_recommendation: (
        RecommendationText
    )

    interview_guidance: RecommendationText


class GapAnalysis(StrictResponseModel):
    supported_requirements: list[
        RequirementText
    ]

    reasonably_derived_requirements: list[
        RequirementText
    ]

    unsupported_requirements: list[
        UnsupportedRequirement
    ]


class CVOptimizationResponse(
    StrictResponseModel
):
    fit_assessment: FitAssessment
    cv_patch: CVPatch | None
    gap_analysis: GapAnalysis
    warnings: list[WarningText]

    @model_validator(mode="after")
    def validate_fit_and_cv_patch(
        self,
    ) -> "CVOptimizationResponse":
        fit_level = self.fit_assessment.level

        if (
            fit_level == "poor"
            and self.cv_patch is not None
        ):
            raise ValueError(
                "cv_patch must be null when "
                "fit_assessment.level is 'poor'."
            )

        if (
            fit_level
            in {"strong", "solid", "stretch"}
            and self.cv_patch is None
        ):
            raise ValueError(
                "cv_patch is required when "
                f"fit_assessment.level is "
                f"'{fit_level}'."
            )

        return self
