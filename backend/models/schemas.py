from pydantic import BaseModel, EmailStr, Field

class ExperienceItem(BaseModel):
    """Represents a single work experience entry."""
    company: str
    role: str
    duration: str
    description: str

class EducationItem(BaseModel):
    """Represents a single education entry."""
    institution: str
    degree: str
    year: str

class CandidateProfile(BaseModel):
    """Structured representation of a parsed resume."""
    name: str = Field(..., description="Full name of the candidate")
    email: EmailStr = Field(..., description="Primary email address")
    skills: list[str] = Field(default_factory=list, description="List of technical and soft skills")
    experience: list[ExperienceItem] = Field(default_factory=list, description="Work history")
    education: list[EducationItem] = Field(default_factory=list, description="Educational background")
    certifications: list[str] = Field(default_factory=list, description="Earned certifications")
    projects: list[str] = Field(default_factory=list, description="Notable projects")
    achievements: list[str] = Field(default_factory=list, description="Awards or major achievements")

class JobDescription(BaseModel):
    """Structured representation of a job requirement."""
    role: str = Field(..., description="Job title")
    mandatory_skills: list[str] = Field(default_factory=list, description="Must-have skills")
    optional_skills: list[str] = Field(default_factory=list, description="Nice-to-have skills")
    experience_required: str = Field(..., description="Required years or level of experience")
    responsibilities: list[str] = Field(default_factory=list, description="Key duties of the role")
    qualifications: list[str] = Field(default_factory=list, description="Required degrees or certifications")
    tools: list[str] = Field(default_factory=list, description="Required software tools")
    frameworks: list[str] = Field(default_factory=list, description="Required technical frameworks")