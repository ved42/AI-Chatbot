from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.config.config import AppConfig


class TestAppConfig(unittest.TestCase):

    def test_app_config_loads_environment_variables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env = {
                "GEMINI_API_KEY": "test-key",
                "SQLITE_DB_PATH": str(Path(temp_dir) / "db.sqlite"),
                "UPLOAD_DIRECTORY": str(Path(temp_dir) / "uploads"),
                "JD_DIRECTORY": str(Path(temp_dir) / "jds"),
                "PARSED_RESUME_DIRECTORY": str(Path(temp_dir) / "parsed_resumes"),
                "PARSED_JD_DIRECTORY": str(Path(temp_dir) / "parsed_jds"),
                "SESSION_DIRECTORY": str(Path(temp_dir) / "sessions"),
                "LOG_LEVEL": "DEBUG",
                "SUPPORTED_FILE_TYPES": "pdf,txt,docx",
            }
            with patch.dict(os.environ, env, clear=False):
                config = AppConfig()
                config.ensure_directories()

                self.assertEqual(config.gemini_api_key, "test-key")
                self.assertEqual(config.sqlite_db_path, Path(temp_dir) / "db.sqlite")
                self.assertEqual(config.log_level, "DEBUG")
                self.assertIn("pdf", config.supported_file_types)
                self.assertTrue(config.upload_directory.exists())
                self.assertTrue(config.jd_directory.exists())
                self.assertTrue(config.parsed_resume_directory.exists())
                self.assertTrue(config.parsed_jd_directory.exists())
                self.assertTrue(config.session_directory.exists())


if __name__ == "__main__":
    unittest.main()
