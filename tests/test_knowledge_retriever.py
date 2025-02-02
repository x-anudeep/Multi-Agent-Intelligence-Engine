from __future__ import annotations

import unittest

from maie.core.config import Settings
from maie.knowledge.retriever import build_default_knowledge_retriever


class KnowledgeRetrieverTests(unittest.TestCase):
    def test_default_retriever_returns_grounding_hits(self) -> None:
        retriever = build_default_knowledge_retriever(Settings())
        self.assertIsNotNone(retriever)

        hits = retriever.retrieve("regulatory disclosures and human review", top_k=2)

        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("Escalation Policy", hits[0].title)


if __name__ == "__main__":
    unittest.main()

