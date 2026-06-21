from __future__ import annotations

from typing import Optional, Dict

from backend.repositories.candidate_repo import get_candidate_by_email
from backend.services.match_service import MatchService


class CandidateInsightAgent:
	"""Produce quick insights for a single candidate."""

	def __init__(self, match_service: Optional[MatchService] = None) -> None:
		self.match_service = match_service or MatchService()

	def skills_summary(self, email: str, db_path: Optional[str] = None) -> Dict:
		candidate = get_candidate_by_email(email=email, db_path=db_path)
		if candidate is None:
			raise ValueError("Candidate not found")
		return {"skill_count": len(candidate.skills), "skills": candidate.skills}


__all__ = ["CandidateInsightAgent"]
