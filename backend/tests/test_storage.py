from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from backend.config.config import AppConfig
from backend.services.storage_service import StorageService


class TestStorageService(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = AppConfig(
            sqlite_db_path=Path(self.temp_dir.name) / "db.sqlite",
            upload_directory=Path(self.temp_dir.name) / "uploads",
            jd_directory=Path(self.temp_dir.name) / "jds",
            parsed_resume_directory=Path(self.temp_dir.name) / "parsed_resumes",
            parsed_jd_directory=Path(self.temp_dir.name) / "parsed_jds",
            session_directory=Path(self.temp_dir.name) / "sessions",
            gemini_api_key="test-key",
        )
        self.storage_service = StorageService(config=self.config)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_save_and_read_text(self) -> None:
        path = self.storage_service.save_text(self.config.upload_directory, "sample.txt", "hello world")
        self.assertTrue(path.exists())
        self.assertEqual(self.storage_service.read_text(path), "hello world")

    def test_save_and_read_bytes(self) -> None:
        content = b"binary data"
        path = self.storage_service.save_bytes(self.config.upload_directory, "sample.bin", content)
        self.assertTrue(path.exists())
        self.assertEqual(path.read_bytes(), content)

    def test_async_read_text(self) -> None:
        path = self.storage_service.save_text(self.config.upload_directory, "async.txt", "async data")
        result = asyncio.run(self.storage_service.read_text_async(path))
        self.assertEqual(result, "async data")


if __name__ == "__main__":
    unittest.main()
