from __future__ import annotations

import os
import unittest
from backend.config.config import AppConfig
from backend.repositories.candidate_repo import init_candidate_db, save_candidate
from backend.repositories.jd_repo import init_jd_db, save_job_description
from backend.models.schemas import CandidateProfile, ExperienceItem, EducationItem, JobDescription
from backend.agent.bulk_agent.ranking_agent.agent import RankingAgent
from backend.agent.bulk_agent.scenario_simulation_agent.agent import ScenarioSimulationAgent
from backend.agent.bulk_agent.search_agent.agent import SearchAgent
from backend.agent.bulk_agent.talent_analytics_agent.agent import TalentAnalyticsAgent
from backend.agent.individual_agent.candidate_profile_agent.agent import CandidateProfileAgent
from backend.agent.individual_agent.candidate_insight_agent.agent import CandidateInsightAgent
from backend.agent.individual_agent.interview_intelligence_agent.agent import InterviewIntelligenceAgent


class TestBulkAgents(unittest.TestCase):

    def setUp(self) -> None:
        os.environ.setdefault("GEMINI_API_KEY", "test-key")
        self.config = AppConfig()
        self.config.ensure_directories()
        db_path = str(self.config.sqlite_db_path)
        init_candidate_db(db_path=db_path)
        init_jd_db(db_path=db_path)

        # Create test candidates
        self.candidate1 = CandidateProfile(
            name="Alice",
            email="alice@example.com",
            skills=["Python", "Docker"],
            experience=[ExperienceItem(company="TechCorp", role="Engineer", duration="3 years", description="Built APIs")],
            education=[EducationItem(institution="State", degree="BSc CS", year="2020")],
        )
        self.candidate2 = CandidateProfile(
            name="Bob",
            email="bob@example.com",
            skills=["Java", "Kubernetes"],
            experience=[ExperienceItem(company="OtherCo", role="Developer", duration="5 years", description="Full stack")],
            education=[EducationItem(institution="University", degree="BSc", year="2018")],
        )

        save_candidate(self.candidate1, db_path=db_path)
        save_candidate(self.candidate2, db_path=db_path)

        self.job = JobDescription(
            role="Backend Engineer",
            mandatory_skills=["Python"],
            optional_skills=["Docker"],
            experience_required="2 years",
            responsibilities=["Build services"],
            qualifications=["BSc CS"],
            tools=["Docker"],
            frameworks=["FastAPI"],
        )
        self.job_id = save_job_description(self.job, db_path=db_path)

    def test_ranking_agent(self) -> None:
        agent = RankingAgent()
        ranked = agent.rank_candidates_for_job(self.job, db_path=str(self.config.sqlite_db_path))
        self.assertGreater(len(ranked), 0)
        self.assertIn("candidate_email", ranked[0])
        self.assertIn("score", ranked[0])
        # Alice should rank higher because she has Python
        emails = [r["candidate_email"] for r in ranked]
        self.assertIn("alice@example.com", emails)

    def test_scenario_simulation_agent(self) -> None:
        agent = ScenarioSimulationAgent()
        base = {"email": "test@example.com", "skills": ["Python"]}
        variations = agent.simulate_variations(base, count=2)
        self.assertEqual(len(variations), 2)
        self.assertIn("+sim0", variations[0]["email"])
        self.assertIn("+sim1", variations[1]["email"])

    def test_search_agent(self) -> None:
        agent = SearchAgent()
        agent.index("doc1", "Python FastAPI Docker", metadata={"type": "skill"})
        agent.index("doc2", "Java Kubernetes", metadata={"type": "skill"})
        results = agent.search("Python", top_k=1)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "doc1")

    def test_talent_analytics_agent(self) -> None:
        agent = TalentAnalyticsAgent()
        dist = agent.skills_distribution(db_path=str(self.config.sqlite_db_path))
        self.assertGreater(len(dist), 0)
        self.assertIn("python", dist)
        self.assertGreater(dist["python"], 0)


class TestIndividualAgents(unittest.TestCase):

    def setUp(self) -> None:
        os.environ.setdefault("GEMINI_API_KEY", "test-key")
        self.config = AppConfig()
        self.config.ensure_directories()
        db_path = str(self.config.sqlite_db_path)
        init_candidate_db(db_path=db_path)

        self.candidate = CandidateProfile(
            name="Charlie",
            email="charlie@example.com",
            skills=["Go", "Rust"],
            experience=[ExperienceItem(company="Startup", role="Founder", duration="2 years", description="Built product")],
            education=[EducationItem(institution="College", degree="BS", year="2022")],
        )
        save_candidate(self.candidate, db_path=db_path)

    def test_candidate_profile_agent(self) -> None:
        agent = CandidateProfileAgent()
        retrieved = agent.get("charlie@example.com", db_path=str(self.config.sqlite_db_path))
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Charlie")

    def test_candidate_insight_agent(self) -> None:
        agent = CandidateInsightAgent()
        insight = agent.skills_summary("charlie@example.com", db_path=str(self.config.sqlite_db_path))
        self.assertIn("skill_count", insight)
        self.assertEqual(insight["skill_count"], 2)
        self.assertIn("Go", insight["skills"])

    def test_interview_intelligence_agent(self) -> None:
        agent = InterviewIntelligenceAgent()
        profile_dict = self.candidate.model_dump()
        questions = agent.suggest_questions(profile_dict)
        self.assertGreater(len(questions), 0)
        self.assertIn("Go", questions[0])


if __name__ == "__main__":
    unittest.main()
