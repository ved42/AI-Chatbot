from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

from backend.config.config import AppConfig
from backend.utils.logger import get_logger


class StorageService:
    """Utility service for local file storage and directory management."""

    def __init__(self, config: Optional[AppConfig] = None, logger: Optional[logging.Logger] = None) -> None:
        self.config = config or AppConfig()
        self.logger = logger or get_logger(__name__, config=self.config)
        self.config.ensure_directories()

    def resolve_path(self, directory: Path, filename: str) -> Path:
        path = directory.joinpath(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def save_bytes(self, directory: Path, filename: str, content: bytes) -> Path:
        path = self.resolve_path(directory, filename)
        with path.open("wb") as file_handle:
            file_handle.write(content)
        self.logger.info("Saved bytes to %s.", path)
        return path

    def save_text(self, directory: Path, filename: str, content: str) -> Path:
        path = self.resolve_path(directory, filename)
        with path.open("w", encoding="utf-8") as file_handle:
            file_handle.write(content)
        self.logger.info("Saved text to %s.", path)
        return path

    def read_text(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"Storage file not found: {path}")
        return path.read_text(encoding="utf-8")

    async def save_bytes_async(self, directory: Path, filename: str, content: bytes) -> Path:
        return await asyncio.to_thread(self.save_bytes, directory, filename, content)

    async def save_text_async(self, directory: Path, filename: str, content: str) -> Path:
        return await asyncio.to_thread(self.save_text, directory, filename, content)

    async def read_text_async(self, path: Path) -> str:
        return await asyncio.to_thread(self.read_text, path)

    def get_resume_path(self, filename: str) -> Path:
        return self.resolve_path(self.config.upload_directory, filename)

    def get_jd_path(self, filename: str) -> Path:
        return self.resolve_path(self.config.jd_directory, filename)
