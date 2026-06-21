from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from backend.models.schemas import CandidateProfile, JobDescription


@dataclass(frozen=True)
class MatchScore:
    overall: float
    skill_match: float
    experience_match: float
    education_match: float
    missing_skills: List[str]


class MatchService:
    """Compute a candidate-to-job match score and skill gap report."""

    @staticmethod
    def _normalize_skills(skills: List[str]) -> List[str]:
        return [skill.strip().lower() for skill in skills if skill and skill.strip()]

    @staticmethod
    def _calculate_skill_match(candidate_skills: List[str], mandatory_skills: List[str], optional_skills: List[str]) -> Dict[str, object]:
        candidate_set = set(MatchService._normalize_skills(candidate_skills))
        mandatory_set = set(MatchService._normalize_skills(mandatory_skills))
        optional_set = set(MatchService._normalize_skills(optional_skills))

        matched_mandatory = candidate_set.intersection(mandatory_set)
        matched_optional = candidate_set.intersection(optional_set)

        mandatory_ratio = len(matched_mandatory) / max(len(mandatory_set), 1)
        optional_ratio = len(matched_optional) / max(len(optional_set), 1)

        missing_skills = sorted(list(mandatory_set.difference(candidate_set)))

        skill_score = (mandatory_ratio * 0.7) + (optional_ratio * 0.3)
        return {
            "skill_score": round(skill_score * 100, 2),
            "mandatory_matched": sorted(matched_mandatory),
            "optional_matched": sorted(matched_optional),
            "missing_skills": missing_skills,
        }

    @staticmethod
    def _calculate_experience_match(candidate: CandidateProfile, job_description: JobDescription) -> float:
        candidate_years = 0.0
        for experience in candidate.experience:
            if experience.duration:
                parts = [part for part in experience.duration.replace("+", "").split() if part.isdigit()]
                if parts:
                    candidate_years += float(parts[0])

        job_years = 0.0
        if job_description.experience_required:
            digits = [part for part in job_description.experience_required.replace("+", "").split() if part.isdigit()]
            if digits:
                job_years = float(digits[0])

        if job_years <= 0:
            return 100.0

        ratio = min(candidate_years / job_years, 1.0)
        return round(ratio * 100, 2)

    @staticmethod
    def _calculate_education_match(candidate: CandidateProfile, job_description: JobDescription) -> float:
        if not job_description.qualifications:
            return 100.0

        candidate_education = " ".join([f"{edu.degree} {edu.institution}" for edu in candidate.education]).lower()
        matched_count = sum(
            1 for requirement in job_description.qualifications if requirement.strip().lower() in candidate_education
        )

        return round((matched_count / len(job_description.qualifications)) * 100, 2)

    def score_candidate(self, candidate: CandidateProfile, job_description: JobDescription) -> MatchScore:
        skill_details = self._calculate_skill_match(
            candidate.skills,
            job_description.mandatory_skills,
            job_description.optional_skills,
        )

        experience_match = self._calculate_experience_match(candidate, job_description)
        education_match = self._calculate_education_match(candidate, job_description)

        overall = round((skill_details["skill_score"] * 0.5) + (experience_match * 0.3) + (education_match * 0.2), 2)

        return MatchScore(
            overall=overall,
            skill_match=skill_details["skill_score"],
            experience_match=experience_match,
            education_match=education_match,
            missing_skills=skill_details["missing_skills"],
        )
