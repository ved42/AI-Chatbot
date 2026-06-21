from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config.config import AppConfig
from backend.repositories.candidate_repo import save_candidate
from backend.services.parser_service import ResumeParserService
from backend.services.storage_service import StorageService
from backend.services.llm_service import LLMService
from backend.services.prompt_loader import PromptLoader
from backend.utils.logger import get_logger

router = APIRouter(prefix="/upload", tags=["upload"])
logger = get_logger(__name__)

config = AppConfig()
storage_service = StorageService(config=config)
llm_service = LLMService(config=config)
prompt_loader = PromptLoader(config=config)
parser_service = ResumeParserService(llm_service=llm_service, prompt_loader=prompt_loader, config=config)


@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a resume and parse it into a CandidateProfile."""
    filename = Path(file.filename).name
    suffix = Path(filename).suffix.lower().strip(".")

    if suffix not in config.supported_file_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    try:
        content = await file.read()
        save_path = storage_service.save_bytes(storage_service.get_resume_path(filename).parent, filename, content)
        raw_text = await storage_service.read_text_async(save_path) if suffix != "pdf" else await parser_service.extract_text_from_file_async(save_path)
        parsed_profile = await parser_service.parse_resume_text_async(raw_text)
        candidate_id = save_candidate(parsed_profile, db_path=str(config.sqlite_db_path))

        return {
            "filename": filename,
            "path": str(save_path),
            "candidate_id": candidate_id,
            "candidate": parsed_profile.model_dump(),
        }
    except Exception as exc:
        logger.error("Failed to upload or parse resume: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to process resume upload.") from exc
