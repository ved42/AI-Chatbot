from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.config.config import AppConfig
from backend.models.schemas import CandidateProfile, ExperienceItem, EducationItem, JobDescription
from backend.repositories.candidate_repo import save_candidate, init_candidate_db
from backend.repositories.jd_repo import save_job_description, init_jd_db


class TestApiMatch(unittest.TestCase):

    def setUp(self) -> None:
        # Ensure required env vars for AppConfig
        import os
        os.environ.setdefault("GEMINI_API_KEY", "test-key")

        # Use the app's configured DB path to keep behavior consistent
        self.config = AppConfig()
        # Ensure directories and DB exist
        self.config.ensure_directories()
        init_candidate_db(db_path=str(self.config.sqlite_db_path))
        init_jd_db(db_path=str(self.config.sqlite_db_path))

    def test_match_endpoint(self) -> None:
        candidate = CandidateProfile(
            name="API Test",
            email="apitest@example.com",
            skills=["Python", "Docker"],
            experience=[ExperienceItem(company="Acme", role="Dev", duration="3 years", description="Work")],
            education=[EducationItem(institution="State", degree="BSc Computer Science", year="2020")],
        )

        job = JobDescription(
            role="Dev",
            mandatory_skills=["Python"],
            optional_skills=["Docker"],
            experience_required="2 years",
            responsibilities=[],
            qualifications=["BSc Computer Science"],
            tools=[],
            frameworks=[],
        )

        # Save candidate and job to DB
        save_candidate(candidate, db_path=str(self.config.sqlite_db_path))
        job_id = save_job_description(job, db_path=str(self.config.sqlite_db_path))

        # Import app after DB setup
        from backend.app import app

        client = TestClient(app)
        resp = client.get(f"/match/candidate/{candidate.email}/job/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["candidate_email"] == candidate.email
        assert data["job_id"] == job_id
        assert "score" in data
        assert "details" in data

    def test_match_candidate_not_found(self) -> None:
        import os
        os.environ.setdefault("GEMINI_API_KEY", "test-key")

        # ensure DB exists but no candidate saved
        self.config.ensure_directories()
        init_candidate_db(db_path=str(self.config.sqlite_db_path))
        init_jd_db(db_path=str(self.config.sqlite_db_path))

        # create a job
        job = JobDescription(
            role="Dev",
            mandatory_skills=["Python"],
            optional_skills=[],
            experience_required="1 year",
            responsibilities=[],
            qualifications=[],
            tools=[],
            frameworks=[],
        )
        job_id = save_job_description(job, db_path=str(self.config.sqlite_db_path))

        from backend.app import app
        client = TestClient(app)

        resp = client.get(f"/match/candidate/nonexistent@example.com/job/{job_id}")
        assert resp.status_code == 404

    def test_match_job_not_found(self) -> None:
        import os
        os.environ.setdefault("GEMINI_API_KEY", "test-key")

        # ensure DB exists and candidate saved
        self.config.ensure_directories()
        init_candidate_db(db_path=str(self.config.sqlite_db_path))
        init_jd_db(db_path=str(self.config.sqlite_db_path))

        candidate = CandidateProfile(
            name="API Test2",
            email="apitest2@example.com",
            skills=["Python"],
            experience=[ExperienceItem(company="Acme", role="Dev", duration="2 years", description="Work")],
            education=[EducationItem(institution="State", degree="BSc", year="2020")],
        )

        save_candidate(candidate, db_path=str(self.config.sqlite_db_path))

        from backend.app import app
        client = TestClient(app)

        resp = client.get(f"/match/candidate/{candidate.email}/job/99999")
        assert resp.status_code == 404


if __name__ == "__main__":
    unittest.main()
