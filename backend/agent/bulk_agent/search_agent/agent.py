from __future__ import annotations

from typing import Optional, List, Dict

from backend.services.vector_service import InMemoryVectorService


class SearchAgent:
	"""Simple search agent using the in-memory vector service."""

	def __init__(self, vector_service: Optional[InMemoryVectorService] = None) -> None:
		self.vector = vector_service or InMemoryVectorService()

	def index(self, doc_id: str, text: str, metadata: Dict | None = None) -> None:
		self.vector.index(doc_id, text, metadata=metadata)

	def search(self, query: str, top_k: int = 5) -> List[Dict]:
		return self.vector.search(query, top_k=top_k)


__all__ = ["SearchAgent"]
