from __future__ import annotations

from typing import Dict
from collections import Counter

from backend.repositories.candidate_repo import get_all_candidates


class TalentAnalyticsAgent:
	"""Compute simple analytics across candidates for reporting."""

	def skills_distribution(self, db_path: str | None = None) -> Dict[str, int]:
		candidates = get_all_candidates(db_path=db_path)
		counter = Counter()
		for c in candidates:
			for s in c.skills:
				counter[s.lower()] += 1
		return dict(counter)


__all__ = ["TalentAnalyticsAgent"]
