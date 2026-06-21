from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from backend.config.config import AppConfig
from backend.models.schemas import CandidateProfile, ExperienceItem, EducationItem, JobDescription
from backend.repositories.jd_repo import save_job_description, init_jd_db
from backend.repositories.candidate_repo import save_candidate, init_candidate_db
from backend.services.match_service import MatchService


class TestMatchService(unittest.TestCase):

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
        self.match_service = MatchService()
        init_candidate_db(db_path=str(self.config.sqlite_db_path))
        init_jd_db(db_path=str(self.config.sqlite_db_path))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_score_candidate_against_job(self) -> None:
        candidate = CandidateProfile(
            name="Jane Doe",
            email="jane.doe@example.com",
            skills=["Python", "AWS", "Docker"],
            experience=[ExperienceItem(company="Acme", role="Engineer", duration="3 years", description="Built APIs")],
            education=[EducationItem(institution="State University", degree="BSc Computer Science", year="2020")],
            certifications=["AWS Certified"],
            projects=["Recruitment app"],
            achievements=["Employee of the month"],
        )
        job_description = JobDescription(
            role="Backend Engineer",
            mandatory_skills=["Python", "Docker"],
            optional_skills=["AWS", "Kubernetes"],
            experience_required="3 years",
            responsibilities=["Build microservices"],
            qualifications=["BSc Computer Science"],
            tools=["Docker"],
            frameworks=["FastAPI"],
        )

        score = self.match_service.score_candidate(candidate, job_description)

        self.assertGreaterEqual(score.overall, 0)
        self.assertEqual(score.missing_skills, [])
        self.assertEqual(score.experience_match, 100.0)
        self.assertEqual(score.education_match, 100.0)


if __name__ == "__main__":
    unittest.main()
