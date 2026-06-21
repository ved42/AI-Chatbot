from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.config.config import AppConfig
from backend.repositories.jd_repo import save_job_description, get_job_description_by_id
from backend.services.parser_service import ResumeParserService
from backend.services.llm_service import LLMService
from backend.services.prompt_loader import PromptLoader
from backend.utils.logger import get_logger

router = APIRouter(prefix="/job-description", tags=["job_description"])
logger = get_logger(__name__)
config = AppConfig()
llm_service = LLMService(config=config)
prompt_loader = PromptLoader(config=config)
parser_service = ResumeParserService(llm_service=llm_service, prompt_loader=prompt_loader, config=config)


@router.post("/parse")
async def parse_job_description(raw_text: str) -> dict[str, Any]:
    try:
        parsed_jd = await parser_service.parse_job_description_text_async(raw_text)
        job_id = save_job_description(parsed_jd, db_path=str(config.sqlite_db_path))
        return {
            "job_id": job_id,
            "job_description": parsed_jd.model_dump(),
        }
    except Exception as exc:
        logger.error("Failed to parse job description: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to parse job description.") from exc


@router.get("/{job_id}")
async def get_job_description(job_id: int) -> dict[str, Any]:
    try:
        jd = get_job_description_by_id(job_id=job_id, db_path=str(config.sqlite_db_path))
        if jd is None:
            raise HTTPException(status_code=404, detail="Job description not found.")
        return jd.model_dump()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to retrieve job description %s: %s", job_id, exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve job description.") from exc
