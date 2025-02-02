from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
import re

from maie.knowledge.documents import KnowledgeChunk, load_knowledge_chunks

if TYPE_CHECKING:
    from maie.core.config import Settings


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


@dataclass(slots=True)
class RetrievalHit:
    source_path: str
    title: str
    excerpt: str
    score: int


class LocalKnowledgeRetriever:
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self.chunks = chunks

    def retrieve(self, query: str, *, top_k: int = 3) -> list[RetrievalHit]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored: list[RetrievalHit] = []
        for chunk in self.chunks:
            overlap = len(query_tokens & chunk.tokens)
            if overlap == 0:
                continue
            scored.append(
                RetrievalHit(
                    source_path=chunk.source_path,
                    title=chunk.title,
                    excerpt=chunk.excerpt,
                    score=overlap,
                )
            )

        scored.sort(key=lambda item: (-item.score, item.title, item.source_path))
        return scored[:top_k]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)}


def build_default_knowledge_retriever(settings: "Settings") -> LocalKnowledgeRetriever | None:
    knowledge_dir = Path(settings.knowledge_dir)
    chunks = load_knowledge_chunks(knowledge_dir)
    if not chunks:
        return None
    return LocalKnowledgeRetriever(chunks)

