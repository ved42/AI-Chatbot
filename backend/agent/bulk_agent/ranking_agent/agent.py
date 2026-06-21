from __future__ import annotations

from typing import Iterable, List, Dict, Optional

from backend.services.match_service import MatchService
from backend.repositories.candidate_repo import get_all_candidates


class RankingAgent:
	"""Rank candidates for a given job using MatchService scoring."""

	def __init__(self, match_service: Optional[MatchService] = None) -> None:
		self.match_service = match_service or MatchService()

	def rank_candidates_for_job(self, job_description, db_path: Optional[str] = None) -> List[Dict]:
		candidates = get_all_candidates(db_path=db_path)
		scored = []
		for c in candidates:
			score = self.match_service.score_candidate(c, job_description)
			scored.append({"candidate_email": c.email, "score": score.overall, "details": score})

		scored.sort(key=lambda x: x["score"], reverse=True)
		return scored


__all__ = ["RankingAgent"]
