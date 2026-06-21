from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from typing import List


class ResumeUploadRequest(BaseModel):
    filename: str = Field(..., description="Name of the uploaded resume file")
    raw_text: str = Field(..., description="Extracted text from the uploaded resume")


class JobDescriptionUploadRequest(BaseModel):
    raw_text: str = Field(..., description="Raw text content of the job description")
