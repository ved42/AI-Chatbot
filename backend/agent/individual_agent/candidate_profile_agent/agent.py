from __future__ import annotations

from typing import Optional

from backend.repositories.candidate_repo import get_candidate_by_email, save_candidate
from backend.models.schemas import CandidateProfile


class CandidateProfileAgent:
	"""Agent for reading and updating candidate profiles."""

	def get(self, email: str, db_path: Optional[str] = None) -> Optional[CandidateProfile]:
		return get_candidate_by_email(email=email, db_path=db_path)

	def save(self, profile: CandidateProfile, db_path: Optional[str] = None) -> int:
		return save_candidate(profile, db_path=db_path)


__all__ = ["CandidateProfileAgent"]
