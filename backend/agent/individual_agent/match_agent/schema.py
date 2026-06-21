from __future__ import annotations

from pydantic import BaseModel
from typing import List


class MatchDetails(BaseModel):
	skill_match: float
	experience_match: float
	education_match: float
	missing_skills: List[str]


class MatchResult(BaseModel):
	candidate_email: str
	job_id: int
	score: float
	details: MatchDetails
