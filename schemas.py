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
    photo: str | None = None
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


# Resume Generation schemas
class ResumeGenerateRequest(BaseModel):
    job_description: str
    job_description_id: int | None = None  # Optional: link to existing JD

    @field_validator("job_description")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip()


class SkillMatch(BaseModel):
    name: str
    matched: bool


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


class ResumeContent(BaseModel):
    personal_info: dict | None = None
    summary: str | None = None
    work_experiences: list[ResumeWorkExperience] = []
    skills: list[ResumeSkill] = []
    education: list[ResumeEducation] = []
    projects: list[ResumeProject] = []


class GeneratedResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: str | None = None
    company_name: str | None = None
    match_score: float | None = None
    job_analysis: JobAnalysis | None = None
    resume: ResumeContent | None = None
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


# Job Description schemas
class JobDescriptionCreate(BaseModel):
    raw_text: str = Field(..., min_length=100)

    @field_validator("raw_text")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip()


class JobDescriptionUpdate(BaseModel):
    title: str | None = Field(None, max_length=100)
    raw_text: str | None = None

    @field_validator("raw_text")
    @classmethod
    def validate_length(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip() if v else v


class JobDescriptionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str | None = None
    raw_text_preview: str
    resume_count: int
    created_at: str
    updated_at: str


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str | None = None
    raw_text: str
    resume_count: int
    created_at: str
    updated_at: str


class JobDescriptionWithResumes(JobDescriptionResponse):
    resumes: list[ResumeHistoryItem] = []


class JobDescriptionVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    raw_text: str
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
