import sqlite3
import json
from typing import Optional
from pathlib import Path

from backend.models.schemas import CandidateProfile, ExperienceItem, EducationItem

# Default database path - can be overridden via environment variables later
DB_PATH = "hiring_platform.db"

def init_candidate_db(db_path: str = DB_PATH) -> None:
    """Initializes the candidates table in the SQLite database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                skills TEXT NOT NULL,
                experience TEXT NOT NULL,
                education TEXT NOT NULL,
                certifications TEXT NOT NULL,
                projects TEXT NOT NULL,
                achievements TEXT NOT NULL
            )
        ''')
        conn.commit()

def save_candidate(candidate: CandidateProfile, db_path: str = DB_PATH) -> int:
    """
    Saves a CandidateProfile to the database.
    Returns the auto-generated row ID.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidates (
                name, email, skills, experience, education, 
                certifications, projects, achievements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name=excluded.name,
                skills=excluded.skills,
                experience=excluded.experience,
                education=excluded.education,
                certifications=excluded.certifications,
                projects=excluded.projects,
                achievements=excluded.achievements
        ''', (
            candidate.name,
            candidate.email,
            json.dumps(candidate.skills),
            json.dumps([exp.model_dump() for exp in candidate.experience]),
            json.dumps([edu.model_dump() for edu in candidate.education]),
            json.dumps(candidate.certifications),
            json.dumps(candidate.projects),
            json.dumps(candidate.achievements)
        ))
        conn.commit()
        return cursor.lastrowid

def get_candidate_by_email(email: str, db_path: str = DB_PATH) -> Optional[CandidateProfile]:
    """
    Retrieves a candidate by their email address.
    Reconstructs and returns a validated CandidateProfile Pydantic model.
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row  # Allows dict-like access to rows
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidates WHERE email = ?', (email,))
        row = cursor.fetchone()

        if not row:
            return None

        # Reconstruct the Pydantic model from the JSON strings
        return CandidateProfile(
            name=row["name"],
            email=row["email"],
            skills=json.loads(row["skills"]),
            experience=[ExperienceItem(**item) for item in json.loads(row["experience"])],
            education=[EducationItem(**item) for item in json.loads(row["education"])],
            certifications=json.loads(row["certifications"]),
            projects=json.loads(row["projects"]),
            achievements=json.loads(row["achievements"])
        )

def get_all_candidates(db_path: str = DB_PATH) -> list[CandidateProfile]:
    """Retrieves all candidates from the database."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidates')
        rows = cursor.fetchall()

        candidates = []
        for row in rows:
            candidates.append(CandidateProfile(
                name=row["name"],
                email=row["email"],
                skills=json.loads(row["skills"]),
                experience=[ExperienceItem(**item) for item in json.loads(row["experience"])],
                education=[EducationItem(**item) for item in json.loads(row["education"])],
                certifications=json.loads(row["certifications"]),
                projects=json.loads(row["projects"]),
                achievements=json.loads(row["achievements"])
            ))
        return candidates