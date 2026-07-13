from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from ai.response_models import (
    ExperienceUpdate,
    SkillText,
    SummaryText,
)


RevisionSection = Literal[
    "professional_summary",
    "experience_updates",
    "skills_to_highlight",
]

RevisionComment = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=1000,
    ),
]


class StrictRevisionModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class RevisionSectionRequest(
    StrictRevisionModel
):
    section: RevisionSection
    comment: RevisionComment


class CVRevisionRequest(
    StrictRevisionModel
):
    application_id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=200,
        ),
    ]

    sections: list[
        RevisionSectionRequest
    ] = Field(
        min_length=1,
        max_length=3,
    )

    @model_validator(mode="after")
    def validate_unique_sections(
        self,
    ) -> "CVRevisionRequest":
        section_names = [
            item.section
            for item in self.sections
        ]

        if (
            len(section_names)
            != len(set(section_names))
        ):
            raise ValueError(
                "Each revision section may be "
                "selected only once."
            )

        return self

    @property
    def requested_sections(
        self,
    ) -> tuple[RevisionSection, ...]:
        return tuple(
            item.section
            for item in self.sections
        )

    def comment_for(
        self,
        section: RevisionSection,
    ) -> str:
        for item in self.sections:
            if item.section == section:
                return item.comment

        raise KeyError(
            f"Section was not requested: {section}"
        )


class CVRevisionResponse(
    StrictRevisionModel
):
    professional_summary: (
        SummaryText | None
    ) = None

    experience_updates: (
        list[ExperienceUpdate] | None
    ) = Field(
        default=None,
        min_length=1,
    )

    skills_to_highlight: (
        list[SkillText] | None
    ) = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    @model_validator(mode="after")
    def validate_provided_sections(
        self,
    ) -> "CVRevisionResponse":
        provided = self.model_fields_set

        if not provided:
            raise ValueError(
                "Revision response must contain "
                "at least one section."
            )

        for field_name in provided:
            if getattr(self, field_name) is None:
                raise ValueError(
                    f"Revision section "
                    f"'{field_name}' cannot be null."
                )

        return self

    @property
    def provided_sections(
        self,
    ) -> tuple[RevisionSection, ...]:
        return tuple(
            field_name
            for field_name in (
                "professional_summary",
                "experience_updates",
                "skills_to_highlight",
            )
            if field_name in self.model_fields_set
        )
