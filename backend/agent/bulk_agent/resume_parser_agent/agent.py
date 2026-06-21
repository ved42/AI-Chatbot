from __future__ import annotations

from typing import Iterable, List, Optional

from backend.services.parser_service import ResumeParserService
from backend.repositories.candidate_repo import save_candidate
from backend.models.schemas import CandidateProfile


class ResumeParserAgent:
	"""Batch resume parsing agent. Uses `ResumeParserService` when provided."""

	def __init__(self, parser_service: Optional[ResumeParserService] = None) -> None:
		self.parser_service = parser_service

	def parse_and_save(self, raw_texts: Iterable[str], db_path: Optional[str] = None) -> List[CandidateProfile]:
		parsed = []
		for text in raw_texts:
			if self.parser_service:
				profile = self.parser_service.parse_resume_text(text)
			else:
				# naive fallback: create a CandidateProfile with minimal fields
				profile = CandidateProfile(name="Unknown", email="unknown@example.com")

			save_candidate(profile, db_path=db_path)
			parsed.append(profile)

		return parsed


__all__ = ["ResumeParserAgent"]

