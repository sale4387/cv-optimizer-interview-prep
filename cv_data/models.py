from pydantic import BaseModel, ConfigDict, Field


class CVBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class PersonalInfo(CVBaseModel):
    full_name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    email: str = Field(min_length=1)
    linkedin: str = Field(min_length=1)


class ProfessionalExperience(CVBaseModel):
    experience_id: str = Field(min_length=1)
    employer: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    location: str = Field(min_length=1)
    start_date: str = Field(min_length=1)
    end_date: str = Field(min_length=1)
    responsibilities: list[str] = Field(min_length=1)
    achievements: list[str] = Field(default_factory=list)


class Project(CVBaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: str = Field(min_length=1)
    description: str = Field(min_length=1)
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)


class Education(CVBaseModel):
    education_id: str = Field(min_length=1)
    institution: str = Field(min_length=1)
    qualification: str = Field(min_length=1)
    start_date: str = Field(min_length=1)
    end_date: str = Field(min_length=1)


class Language(CVBaseModel):
    language: str = Field(min_length=1)
    level: str = Field(min_length=1)


class CVProfile(CVBaseModel):
    profile_id: str = Field(min_length=1)
    cv_version: str = Field(min_length=1)
    personal_info: PersonalInfo
    professional_summary: str = Field(min_length=1)
    core_skills: list[str] = Field(min_length=1)
    professional_experience: list[ProfessionalExperience] = Field(min_length=1)
    projects: list[Project] = Field(default_factory=list)
    education: list[Education] = Field(min_length=1)
    languages: list[Language] = Field(min_length=1)
    tools_and_technologies: list[str] = Field(default_factory=list)