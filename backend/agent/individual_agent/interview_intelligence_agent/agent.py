from __future__ import annotations

from typing import Dict, List


class InterviewIntelligenceAgent:
	"""Provide interview question suggestions based on candidate profile."""

	def suggest_questions(self, candidate_profile: Dict) -> List[str]:
		skills = candidate_profile.get("skills", [])
		questions = [f"Tell me about your experience with {s}." for s in skills[:5]]
		if not questions:
			questions.append("Tell me about your most relevant project.")
		return questions


__all__ = ["InterviewIntelligenceAgent"]
