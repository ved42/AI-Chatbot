from __future__ import annotations

import os
from pathlib import Path
from backend.config.config import AppConfig
from backend.repositories.candidate_repo import init_candidate_db, save_candidate
from backend.repositories.jd_repo import init_jd_db, save_job_description
from backend.models.schemas import CandidateProfile, ExperienceItem, EducationItem, JobDescription


def seed_demo_data(config: AppConfig | None = None) -> None:
    """Seed the local SQLite DB with demo candidate(s) and job(s)."""
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    config = config or AppConfig()
    config.ensure_directories()

    db_path = str(config.sqlite_db_path)
    init_candidate_db(db_path=db_path)
    init_jd_db(db_path=db_path)

    candidate = CandidateProfile(
        name="Seed Candidate",
        email="seed@example.com",
        skills=["Python", "FastAPI", "Docker"],
        experience=[ExperienceItem(company="SeedCo", role="Engineer", duration="4 years", description="Built services")],
        education=[EducationItem(institution="State Univ", degree="BSc Computer Science", year="2018")],
    )

    job = JobDescription(
        role="Backend Engineer",
        mandatory_skills=["Python", "Docker"],
        optional_skills=["FastAPI"],
        experience_required="3 years",
        responsibilities=["Build APIs"],
        qualifications=["BSc Computer Science"],
        tools=["Docker"],
        frameworks=["FastAPI"],
    )

    save_candidate(candidate, db_path=db_path)
    job_id = save_job_description(job, db_path=db_path)
    print(f"Seeded candidate {candidate.email} and job id {job_id} into {db_path}")


if __name__ == "__main__":
    seed_demo_data()
