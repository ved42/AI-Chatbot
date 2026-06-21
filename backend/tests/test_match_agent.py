from __future__ import annotations

import os
import unittest
from backend.agent.individual_agent.match_agent.agent import MatchAgent
from backend.cli.seed_demo import seed_demo_data
from backend.config.config import AppConfig


class TestMatchAgent(unittest.TestCase):

    def setUp(self) -> None:
        os.environ.setdefault("GEMINI_API_KEY", "test-key")
        self.config = AppConfig()
        seed_demo_data(self.config)
        self.agent = MatchAgent()

    def test_match_seed(self) -> None:
        # Seed creates job with id 7 in earlier runs; retrieve latest job by matching
        res = self.agent.match_candidate_to_job("seed@example.com", 7, db_path=str(self.config.sqlite_db_path))
        self.assertEqual(res["candidate_email"], "seed@example.com")
        self.assertIn("score", res)


if __name__ == "__main__":
    unittest.main()
