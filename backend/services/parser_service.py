from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ValidationError

from backend.config.config import AppConfig
from backend.models.schemas import CandidateProfile, JobDescription
from backend.services.llm_service import LLMService
from backend.services.prompt_loader import PromptLoader
from backend.utils.logger import get_logger


class TextExtractionService:
    """Extract text from PDF files and from text files."""

    def __init__(self, config: Optional[AppConfig] = None, logger: Optional[logging.Logger] = None) -> None:
        self.config = config or AppConfig()
        self.logger = logger or get_logger(__name__, config=self.config)

    def extract_text_from_pdf(self, file_path: Path | str) -> str:
        try:
            import fitz
        except ImportError as exc:
            raise ImportError("PyMuPDF is required for PDF extraction. Install pymupdf.") from exc

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        text_chunks: list[str] = []
        with fitz.open(path) as document:
            for page in document:
                page_text = page.get_text("text")
                if page_text:
                    text_chunks.append(page_text.strip())

        result = "\n\n".join(text_chunks).strip()
        self.logger.debug("Extracted %d characters from PDF %s.", len(result), path)
        return result

    def extract_text_from_file(self, file_path: Path | str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() == ".pdf":
            return self.extract_text_from_pdf(path)

        return path.read_text(encoding="utf-8")

    async def extract_text_from_file_async(self, file_path: Path | str) -> str:
        return await asyncio.to_thread(self.extract_text_from_file, file_path)


class ResumeParserService:
    """Service to parse resumes and job descriptions into validated domain models."""

    def __init__(
        self,
        llm_service: LLMService,
        prompt_loader: PromptLoader,
        config: Optional[AppConfig] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.config = config or AppConfig()
        self.logger = logger or get_logger(__name__, config=self.config)
        self.llm_service = llm_service
        self.prompt_loader = prompt_loader

    def _load_system_prompt(self, prompt_path: str) -> str:
        try:
            return self.prompt_loader.get_prompt(prompt_path, "system_prompt")
        except FileNotFoundError:
            raise
        except Exception as exc:
            self.logger.error("Failed to load system prompt from %s: %s", prompt_path, exc)
            raise

    def parse_resume_text(self, raw_resume_text: str) -> CandidateProfile:
        prompt_path = "ingestion/resume_parser/prompt.yaml"
        system_prompt = self._load_system_prompt(prompt_path)

        try:
            parsed_profile = self.llm_service.generate_json(
                prompt=raw_resume_text,
                response_schema=CandidateProfile,
                system_prompt=system_prompt,
            )
            self.logger.info("Parsed resume text into CandidateProfile for %s.", parsed_profile.name)
            return parsed_profile
        except ValidationError as exc:
            self.logger.error("CandidateProfile validation failed: %s", exc)
            raise RuntimeError("Failed to validate parsed resume data.") from exc
        except Exception as exc:
            self.logger.error("Resume parsing failed: %s", exc)
            raise

    async def parse_resume_text_async(self, raw_resume_text: str) -> CandidateProfile:
        prompt_path = "ingestion/resume_parser/prompt.yaml"
        system_prompt = self._load_system_prompt(prompt_path)

        try:
            parsed_profile = await self.llm_service.generate_json_async(
                prompt=raw_resume_text,
                response_schema=CandidateProfile,
                system_prompt=system_prompt,
            )
            self.logger.info("Parsed resume text into CandidateProfile for %s.", parsed_profile.name)
            return parsed_profile
        except ValidationError as exc:
            self.logger.error("CandidateProfile validation failed: %s", exc)
            raise RuntimeError("Failed to validate parsed resume data.") from exc
        except Exception as exc:
            self.logger.error("Resume parsing failed: %s", exc)
            raise

    def parse_job_description_text(self, raw_jd_text: str) -> JobDescription:
        prompt_path = "ingestion/jd_parser/prompt.yaml"
        system_prompt = self._load_system_prompt(prompt_path)

        try:
            parsed_jd = self.llm_service.generate_json(
                prompt=raw_jd_text,
                response_schema=JobDescription,
                system_prompt=system_prompt,
            )
            self.logger.info("Parsed JD text into JobDescription for %s.", parsed_jd.role)
            return parsed_jd
        except ValidationError as exc:
            self.logger.error("JobDescription validation failed: %s", exc)
            raise RuntimeError("Failed to validate parsed job description data.") from exc
        except Exception as exc:
            self.logger.error("JD parsing failed: %s", exc)
            raise

    async def parse_job_description_text_async(self, raw_jd_text: str) -> JobDescription:
        prompt_path = "ingestion/jd_parser/prompt.yaml"
        system_prompt = self._load_system_prompt(prompt_path)

        try:
            parsed_jd = await self.llm_service.generate_json_async(
                prompt=raw_jd_text,
                response_schema=JobDescription,
                system_prompt=system_prompt,
            )
            self.logger.info("Parsed JD text into JobDescription for %s.", parsed_jd.role)
            return parsed_jd
        except ValidationError as exc:
            self.logger.error("JobDescription validation failed: %s", exc)
            raise RuntimeError("Failed to validate parsed job description data.") from exc
        except Exception as exc:
            self.logger.error("JD parsing failed: %s", exc)
            raise
