from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


# Personal Info schemas
class PersonalInfoUpdate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    summary: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email address")
        return v


class PersonalInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    summary: str | None = None
    updated_at: str | None = None


# Work Experience schemas
class WorkExperienceCreate(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    location: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("Invalid date format. Use YYYY-MM")
        return v


class WorkExperienceUpdate(WorkExperienceCreate):
    pass


class WorkExperience(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    title: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    location: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# Education schemas
class EducationCreate(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_year: int | None = None
    gpa: float | None = None
    notes: str | None = None

    @field_validator("graduation_year")
    @classmethod
    def validate_graduation_year(cls, v: int | None) -> int | None:
        if v is not None and (v < 1900 or v > 2100):
            raise ValueError("Graduation year must be between 1900 and 2100")
        return v


class EducationUpdate(EducationCreate):
    pass


class Education(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_year: int | None = None
    gpa: float | None = None
    notes: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# Skill schemas
class SkillCreate(BaseModel):
    names: str  # Comma-separated skill names


class Skill(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# Project schemas
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    technologies: str | None = None
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("Invalid date format. Use YYYY-MM")
        return v


class ProjectUpdate(ProjectCreate):
    pass


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    technologies: str | None = None
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
