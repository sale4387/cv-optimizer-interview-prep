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


PrepStatus = Literal[
    "complete",
    "limited",
]

QuestionCategory = Literal[
    "cv_experience",
    "job_requirement",
    "company_context",
    "gap_or_risk",
    "behavioral",
    "technical_or_domain",
    "motivation",
]

RiskLevel = Literal[
    "low",
    "medium",
    "high",
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
        min_length=10,
        max_length=1500,
    ),
]

LongText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=20,
        max_length=3000,
    ),
]


class StrictInterviewPrepModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class PositioningGuidance(
    StrictInterviewPrepModel
):
    summary: LongText

    focus_points: list[
        MediumText
    ] = Field(min_length=1, max_length=8)

    avoid_overstating: list[
        MediumText
    ] = Field(default_factory=list, max_length=8)


class SuggestedAnswerDirection(
    StrictInterviewPrepModel
):
    angle: MediumText

    key_points: list[
        MediumText
    ] = Field(min_length=1, max_length=6)

    example_focus: MediumText


class InterviewQuestion(
    StrictInterviewPrepModel
):
    question_id: ShortText
    category: QuestionCategory
    question: MediumText
    why_this_matters: MediumText

    evidence_to_use: list[
        MediumText
    ] = Field(min_length=1, max_length=8)

    suggested_answer_directions: list[
        SuggestedAnswerDirection
    ] = Field(min_length=1, max_length=3)

    preparation_note: MediumText
    risk_level: RiskLevel


class ExperienceCheckpoint(
    StrictInterviewPrepModel
):
    emphasized_area: MediumText
    supporting_cv_evidence: MediumText

    likely_follow_up_questions: list[
        MediumText
    ] = Field(min_length=1, max_length=6)

    preparation_needed: MediumText


class CompanySpecificTalkingPoint(
    StrictInterviewPrepModel
):
    topic: MediumText
    why_relevant: MediumText
    how_to_use: MediumText


class CandidateQuestionToAsk(
    StrictInterviewPrepModel
):
    question: MediumText
    reason: MediumText


GENERIC_QUESTION_STARTS = (
    "tell me about yourself",
    "walk me through your cv",
    "walk me through your resume",
)

GENERIC_QUESTION_EXACT = {
    "why do you want this job",
    "what are your strengths",
    "what are your weaknesses",
    "where do you see yourself in five years",
}


def _normalize_question(
    question: str,
) -> str:
    return (
        question.lower()
        .strip()
        .rstrip("?!.")
        .replace("  ", " ")
    )


class InterviewPreparationReport(
    StrictInterviewPrepModel
):
    interview_prep_id: ShortText
    application_id: ShortText
    prep_status: PrepStatus

    positioning_guidance: PositioningGuidance

    questions: list[
        InterviewQuestion
    ] = Field(min_length=10, max_length=15)

    experience_checkpoints: list[
        ExperienceCheckpoint
    ] = Field(min_length=1, max_length=10)

    company_specific_talking_points: list[
        CompanySpecificTalkingPoint
    ] = Field(default_factory=list, max_length=10)

    candidate_questions_to_ask: list[
        CandidateQuestionToAsk
    ] = Field(min_length=1, max_length=10)

    limitations: list[
        MediumText
    ] = Field(default_factory=list, max_length=10)

    generated_at: datetime

    @model_validator(mode="after")
    def validate_questions(
        self,
    ) -> "InterviewPreparationReport":
        seen_questions: set[str] = set()

        for question in self.questions:
            normalized = _normalize_question(
                question.question
            )

            if normalized in seen_questions:
                raise ValueError(
                    "Interview questions must not be duplicated."
                )

            seen_questions.add(normalized)

            if normalized in GENERIC_QUESTION_EXACT:
                raise ValueError(
                    "Generic interview questions must be replaced "
                    "with personalized guidance."
                )

            if any(
                normalized.startswith(start)
                for start in GENERIC_QUESTION_STARTS
            ):
                raise ValueError(
                    "Tell-me-about-yourself style questions belong "
                    "in positioning guidance, not in the question list."
                )

        if (
            self.prep_status == "limited"
            and not self.limitations
        ):
            raise ValueError(
                "Limited interview preparation requires "
                "at least one limitation."
            )

        return self
