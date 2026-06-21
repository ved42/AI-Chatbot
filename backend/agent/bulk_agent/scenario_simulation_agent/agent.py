from __future__ import annotations

from typing import List, Dict


class ScenarioSimulationAgent:
	"""Generate candidate/job matching scenarios for testing and analytics."""

	def simulate_variations(self, base_candidate: Dict, count: int = 3) -> List[Dict]:
		results = []
		for i in range(count):
			c = base_candidate.copy()
			c["email"] = f"{c.get('email','user')}+sim{i}@example.com"
			results.append(c)
		return results


__all__ = ["ScenarioSimulationAgent"]
