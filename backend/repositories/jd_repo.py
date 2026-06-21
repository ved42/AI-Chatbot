from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Optional

from backend.models.schemas import JobDescription


def init_jd_db(db_path: str | Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                mandatory_skills TEXT NOT NULL,
                optional_skills TEXT NOT NULL,
                experience_required TEXT NOT NULL,
                responsibilities TEXT NOT NULL,
                qualifications TEXT NOT NULL,
                tools TEXT NOT NULL,
                frameworks TEXT NOT NULL
            )
        ''')
        conn.commit()


def save_job_description(job_description: JobDescription, db_path: str | Path) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO job_descriptions (
                role, mandatory_skills, optional_skills, experience_required,
                responsibilities, qualifications, tools, frameworks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_description.role,
            json.dumps(job_description.mandatory_skills),
            json.dumps(job_description.optional_skills),
            job_description.experience_required,
            json.dumps(job_description.responsibilities),
            json.dumps(job_description.qualifications),
            json.dumps(job_description.tools),
            json.dumps(job_description.frameworks),
        ))
        conn.commit()
        return cursor.lastrowid


def get_job_description_by_id(job_description_id: int, db_path: str | Path) -> Optional[JobDescription]:
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_descriptions WHERE id = ?', (job_description_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        return JobDescription(
            role=row['role'],
            mandatory_skills=json.loads(row['mandatory_skills']),
            optional_skills=json.loads(row['optional_skills']),
            experience_required=row['experience_required'],
            responsibilities=json.loads(row['responsibilities']),
            qualifications=json.loads(row['qualifications']),
            tools=json.loads(row['tools']),
            frameworks=json.loads(row['frameworks']),
        )
