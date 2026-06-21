from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app import app
from backend.config.config import AppConfig


class TestApi(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = AppConfig(
            gemini_api_key="test-key",
            sqlite_db_path=Path(self.temp_dir.name) / "db.sqlite",
            upload_directory=Path(self.temp_dir.name) / "uploads",
            jd_directory=Path(self.temp_dir.name) / "jds",
            parsed_resume_directory=Path(self.temp_dir.name) / "parsed_resumes",
            parsed_jd_directory=Path(self.temp_dir.name) / "parsed_jds",
            session_directory=Path(self.temp_dir.name) / "sessions",
        )
        os.environ["GEMINI_API_KEY"] = "test-key"
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        os.environ.pop("GEMINI_API_KEY", None)

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
