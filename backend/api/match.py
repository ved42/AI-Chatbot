from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.config.config import AppConfig
from backend.models.schemas import CandidateProfile, JobDescription
from backend.repositories.candidate_repo import get_candidate_by_email
from backend.repositories.jd_repo import get_job_description_by_id
from backend.services.match_service import MatchService
from backend.utils.logger import get_logger

router = APIRouter(prefix="/match", tags=["match"])
logger = get_logger(__name__)
config = AppConfig()
match_service = MatchService()


@router.get("/candidate/{email}/job/{job_id}")
async def match_candidate_to_job(email: str, job_id: int) -> dict[str, object]:
    try:
        candidate = get_candidate_by_email(email=email, db_path=str(config.sqlite_db_path))
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found.")

        job_description = get_job_description_by_id(job_description_id=job_id, db_path=str(config.sqlite_db_path))
        if job_description is None:
            raise HTTPException(status_code=404, detail="Job description not found.")

        score = match_service.score_candidate(candidate, job_description)
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
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to score candidate %s against job %s: %s", email, job_id, exc)
        raise HTTPException(status_code=500, detail="Failed to match candidate to job.") from exc
