from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


@dataclass(slots=True)
class KnowledgeChunk:
    source_path: str
    title: str
    excerpt: str
    tokens: set[str] = field(default_factory=set)


def load_knowledge_chunks(root_dir: str | Path) -> list[KnowledgeChunk]:
    root = Path(root_dir)
    if not root.exists():
        return []

    chunks: list[KnowledgeChunk] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".md", ".txt"} or not path.is_file():
            continue
        raw_text = path.read_text(encoding="utf-8").strip()
        if not raw_text:
            continue
        paragraphs = [block.strip() for block in raw_text.split("\n\n") if block.strip()]
        title = paragraphs[0].splitlines()[0].lstrip("# ").strip()
        for index, paragraph in enumerate(paragraphs):
            excerpt = " ".join(line.strip() for line in paragraph.splitlines())
            if index == 0 and excerpt.lstrip("# ").strip() == title:
                continue
            chunks.append(
                KnowledgeChunk(
                    source_path=str(path),
                    title=title,
                    excerpt=excerpt[:320],
                    tokens=_tokenize(excerpt),
                )
            )
    return chunks


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)}
