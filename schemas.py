from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class CEFRLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


# User schemas
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    summary: str | None = None
    photo: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class UserUpdate(BaseModel):
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


# Language schemas
class LanguageCreate(BaseModel):
    name: str
    level: CEFRLevel


class LanguageUpdate(BaseModel):
    name: str
    level: CEFRLevel


class Language(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    level: str
    display_order: int = 0
    created_at: str | None = None
    updated_at: str | None = None


# Resume Generation schemas
class ResumeGenerateRequest(BaseModel):
    job_description: str
    job_id: int | None = None  # Optional: link to existing job
    language: str = "en"

    @field_validator("job_description")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip()

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in ("en", "fr", "nl"):
            raise ValueError("Language must be en, fr, or nl")
        return v


class SkillMatch(BaseModel):
    """Skill matching result from job analysis."""

    name: str
    matched: bool  # Whether user has this skill (boolean). Distinct from ResumeHistoryItem.match_score (percentage).


class JobAnalysis(BaseModel):
    required_skills: list[SkillMatch] = []
    preferred_skills: list[SkillMatch] = []
    experience_years: dict | None = None
    education: dict | None = None


class ResumeWorkExperience(BaseModel):
    id: int
    company: str
    title: str
    start_date: str
    end_date: str | None = None
    description: str | None = None
    match_reasons: list[str] = []
    included: bool = True
    order: int = 0


class ResumeSkill(BaseModel):
    name: str
    matched: bool
    included: bool = True


class ResumeEducation(BaseModel):
    id: int
    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_year: int | None = None
    included: bool = True


class ResumeProject(BaseModel):
    id: int
    name: str
    description: str | None = None
    technologies: str | None = None
    included: bool = False


class ResumeLanguage(BaseModel):
    id: int
    name: str
    level: str
    included: bool = True


class ResumeContent(BaseModel):
    personal_info: dict | None = None
    summary: str | None = None
    work_experiences: list[ResumeWorkExperience] = []
    skills: list[ResumeSkill] = []
    education: list[ResumeEducation] = []
    projects: list[ResumeProject] = []
    languages: list[ResumeLanguage] = []


class GeneratedResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: str | None = None
    company_name: str | None = None
    match_score: float | None = None
    job_analysis: JobAnalysis | None = None
    resume: ResumeContent | None = None
    language: str = "en"
    created_at: str | None = None


class ResumeHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: str | None = None
    company_name: str | None = None
    match_score: float | None = None
    created_at: str | None = None


class ResumeUpdateRequest(BaseModel):
    resume: ResumeContent


class CompleteProfile(BaseModel):
    personal_info: dict | None = None
    work_experiences: list[dict] = []
    education: list[dict] = []
    skills: list[dict] = []
    projects: list[dict] = []
    languages: list[dict] = []


# Job schemas
class JobCreate(BaseModel):
    original_text: str = Field(..., min_length=100)

    @field_validator("original_text")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip()


class JobUpdate(BaseModel):
    title: str | None = Field(None, max_length=100)
    original_text: str | None = None

    @field_validator("original_text")
    @classmethod
    def validate_length(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip() if v else v


class JobListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str | None = None
    text_preview: str
    resume_count: int
    created_at: str
    updated_at: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str | None = None
    original_text: str
    resume_count: int
    created_at: str
    updated_at: str


class JobWithResumes(JobResponse):
    resumes: list[ResumeHistoryItem] = []


class JobVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    original_text: str
    created_at: str


# Photo schemas
class PhotoUpload(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image data URL")

    @field_validator("image_data")
    @classmethod
    def validate_image_data(cls, v: str) -> str:
        if not re.match(r"^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$", v):
            raise ValueError("Invalid image data format")
        # 10MB file becomes ~13.3MB as base64, allow 15MB for safety
        if len(v) > 15_000_000:
            raise ValueError("Image data too large")
        return v


class PhotoResponse(BaseModel):
    image_data: str | None = None


# Profile Import schemas
class PersonalInfoImport(BaseModel):
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


class WorkExperienceImport(BaseModel):
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


class EducationImport(BaseModel):
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


class SkillImport(BaseModel):
    name: str


class ProjectImport(BaseModel):
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


class LanguageImport(BaseModel):
    name: str
    level: CEFRLevel


class ProfileImport(BaseModel):
    personal_info: PersonalInfoImport
    work_experiences: list[WorkExperienceImport] = []
    education: list[EducationImport] = []
    skills: list[SkillImport] = []
    projects: list[ProjectImport] = []
    languages: list[LanguageImport] = []


class ProfileImportResponse(BaseModel):
    message: str
    counts: dict[str, int]
