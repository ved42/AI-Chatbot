from __future__ import annotations

from typing import List, Dict, Any


class InMemoryVectorService:
    """A minimal in-memory vector-like store for demo/testing purposes.

    This is not a real semantic search engine; it's sufficient for local
    development and unit tests that don't rely on external vector DBs.
    """

    def __init__(self) -> None:
        self._store: List[Dict[str, Any]] = []

    def index(self, doc_id: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        self._store.append({"id": doc_id, "text": text, "metadata": metadata or {}})

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # naive substring scoring by length of match
        results = []
        q = query.lower()
        for item in self._store:
            score = 0
            if q in item["text"].lower():
                score = 1.0
            results.append({"id": item["id"], "score": score, "metadata": item["metadata"]})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]


__all__ = ["InMemoryVectorService"]
