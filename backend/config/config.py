from __future__ import annotations

from pathlib import Path
from typing import Set

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.5-flash", env="GEMINI_MODEL")
    gemini_temperature: float = Field(0.0, env="GEMINI_TEMPERATURE")
    gemini_top_p: float = Field(1.0, env="GEMINI_TOP_P")
    gemini_top_k: int = Field(1, env="GEMINI_TOP_K")
    gemini_max_output_tokens: int = Field(1024, env="GEMINI_MAX_OUTPUT_TOKENS")

    sqlite_db_path: Path = Field(Path("backend/data/hiring_platform.db"), env="SQLITE_DB_PATH")
    upload_directory: Path = Field(Path("backend/data/resumes"), env="UPLOAD_DIRECTORY")
    jd_directory: Path = Field(Path("backend/data/jds"), env="JD_DIRECTORY")
    parsed_resume_directory: Path = Field(Path("backend/data/parsed_resumes"), env="PARSED_RESUME_DIRECTORY")
    parsed_jd_directory: Path = Field(Path("backend/data/parsed_jds"), env="PARSED_JD_DIRECTORY")
    session_directory: Path = Field(Path("backend/data/sessions"), env="SESSION_DIRECTORY")

    log_level: str = Field("INFO", env="LOG_LEVEL")
    supported_file_types: str | Set[str] = Field("pdf,docx,txt", env="SUPPORTED_FILE_TYPES")
    model_retry_attempts: int = Field(2, env="MODEL_RETRY_ATTEMPTS")
    model_retry_backoff_seconds: float = Field(1.0, env="MODEL_RETRY_BACKOFF_SECONDS")

    @validator(
        "supported_file_types",
        pre=True,
    )
    def parse_supported_file_types(cls, value: str | Set[str]) -> Set[str]:
        if isinstance(value, str):
            return {item.strip().lower() for item in value.split(",") if item.strip()}
        return {item.lower() for item in value}

    @validator(
        "sqlite_db_path",
        "upload_directory",
        "jd_directory",
        "parsed_resume_directory",
        "parsed_jd_directory",
        "session_directory",
        pre=True,
    )
    def ensure_path(cls, value: str | Path) -> Path:
        return Path(value)

    def ensure_directories(self) -> None:
        """Create configured local directories for storage if they do not exist."""
        for path in [
            self.upload_directory,
            self.jd_directory,
            self.parsed_resume_directory,
            self.parsed_jd_directory,
            self.session_directory,
            self.sqlite_db_path.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)
