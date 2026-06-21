from __future__ import annotations

from typing import Optional
import json

from backend.models.schemas import CandidateProfile, JobDescription
from backend.repositories.candidate_repo import get_candidate_by_email
from backend.repositories.jd_repo import get_job_description_by_id
from backend.services.match_service import MatchService
from backend.services.prompt_loader import PromptLoader
from backend.agent.individual_agent.match_agent.schema import MatchResult
from backend.services.llm_service import LLMService


class MatchAgent:
    """Lightweight agent that orchestrates matching a candidate to a job.

    This wraps repository lookups and the `MatchService` scoring logic so
    higher-level callers (CLI, orchestration layers) can reuse a single API.
    """

    def __init__(
        self,
        match_service: Optional[MatchService] = None,
        llm_service: Optional[LLMService] = None,
        prompt_loader: Optional[PromptLoader] = None,
    ) -> None:
        self.match_service = match_service or MatchService()
        self.llm_service = llm_service
        self.prompt_loader = prompt_loader or PromptLoader()

    def match_candidate_to_job(self, email: str, job_id: int, db_path: Optional[str] = None, use_llm: bool = False) -> dict:
        """Return a dict with candidate, job_id and matching score/details.

        Raises ValueError when candidate or job are not found.
        """
        candidate: CandidateProfile | None = get_candidate_by_email(email=email, db_path=db_path)
        if candidate is None:
            raise ValueError(f"Candidate not found: {email}")

        job: JobDescription | None = get_job_description_by_id(job_description_id=job_id, db_path=db_path)
        if job is None:
            raise ValueError(f"Job description not found: {job_id}")

        # If configured to use an LLM, attempt to generate structured JSON and validate it
        if use_llm and self.llm_service is not None:
            try:
                candidate_json = json.dumps(candidate.model_dump())
                job_json = json.dumps(job.model_dump())
                prompt = self.prompt_loader.load_and_render(
                    "prompt.yaml", "match_prompt", candidate_json=candidate_json, job_json=job_json
                )
                # Ask the LLM to produce JSON conforming to MatchResult schema
                result_model = self.llm_service.generate_json(prompt=prompt, response_schema=MatchResult)
                return result_model.model_dump()
            except Exception:
                # Fall back to deterministic scoring on any failure
                pass

        score = self.match_service.score_candidate(candidate, job)

        return {
            "candidate_email": candidate.email,
            "job_id": job_id,
            "score": score.overall,
            "details": {
                "skill_match": score.skill_match,
                "experience_match": score.experience_match,
                "education_match": score.education_match,
                "missing_skills": score.missing_skills,
            },
        }


__all__ = ["MatchAgent"]
