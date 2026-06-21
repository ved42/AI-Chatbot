from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from backend.config.config import AppConfig
from backend.repositories.candidate_repo import get_candidate_by_email, get_all_candidates
from backend.utils.logger import get_logger

router = APIRouter(prefix="/candidate", tags=["candidate"])
logger = get_logger(__name__)
config = AppConfig()


@router.get("/all", response_model=List[dict])
async def list_candidates() -> List[dict]:
    try:
        candidates = get_all_candidates(db_path=str(config.sqlite_db_path))
        return [candidate.model_dump() for candidate in candidates]
    except Exception as exc:
        logger.error("Failed to list candidates: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve candidates.") from exc


@router.get("/{email}")
async def get_candidate(email: str) -> dict:
    try:
        candidate = get_candidate_by_email(email=email, db_path=str(config.sqlite_db_path))
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found.")
        return candidate.model_dump()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to retrieve candidate %s: %s", email, exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve candidate.") from exc
