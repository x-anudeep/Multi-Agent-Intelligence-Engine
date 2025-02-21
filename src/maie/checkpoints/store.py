from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from maie.graph.state import WorkflowState, serialize_state


@dataclass(slots=True)
class CheckpointRecord:
    workflow_id: str
    label: str
    state: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "label": self.label,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
        }


class InMemoryCheckpointStore:
    def __init__(self) -> None:
        self._store: dict[str, list[CheckpointRecord]] = {}

    def save(self, workflow_id: str, label: str, state: WorkflowState) -> CheckpointRecord:
        record = CheckpointRecord(
            workflow_id=workflow_id,
            label=label,
            state=serialize_state(state),
        )
        self._store.setdefault(workflow_id, []).append(record)
        return record

    def load(self, workflow_id: str) -> list[CheckpointRecord]:
        return list(self._store.get(workflow_id, []))


class JsonFileCheckpointStore:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)

    def save(self, workflow_id: str, label: str, state: WorkflowState) -> CheckpointRecord:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        record = CheckpointRecord(
            workflow_id=workflow_id,
            label=label,
            state=serialize_state(state),
        )
        target = self.base_dir / f"{workflow_id}.jsonl"
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict()))
            handle.write("\n")
        return record

    def load(self, workflow_id: str) -> list[CheckpointRecord]:
        target = self.base_dir / f"{workflow_id}.jsonl"
        if not target.exists():
            return []
        records: list[CheckpointRecord] = []
        for line in target.read_text(encoding="utf-8").splitlines():
            payload = json.loads(line)
            records.append(
                CheckpointRecord(
                    workflow_id=str(payload["workflow_id"]),
                    label=str(payload["label"]),
                    state=dict(payload["state"]),
                    created_at=datetime.fromisoformat(str(payload["created_at"])),
                )
            )
        return records

    def get_path(self, workflow_id: str) -> Path:
        return self.base_dir / f"{workflow_id}.jsonl"


class SQLiteCheckpointStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def save(self, workflow_id: str, label: str, state: WorkflowState) -> CheckpointRecord:
        record = CheckpointRecord(
            workflow_id=workflow_id,
            label=label,
            state=serialize_state(state),
        )
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO workflow_checkpoints (workflow_id, label, state_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    record.workflow_id,
                    record.label,
                    json.dumps(record.state),
                    record.created_at.isoformat(),
                ),
            )
        return record

    def load(self, workflow_id: str) -> list[CheckpointRecord]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT workflow_id, label, state_json, created_at
                FROM workflow_checkpoints
                WHERE workflow_id = ?
                ORDER BY id ASC
                """,
                (workflow_id,),
            ).fetchall()
        return [
            CheckpointRecord(
                workflow_id=str(row[0]),
                label=str(row[1]),
                state=json.loads(str(row[2])),
                created_at=datetime.fromisoformat(str(row[3])),
            )
            for row in rows
        ]

    def get_path(self, workflow_id: str) -> Path:
        return self.database_path

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )


class PostgresCheckpointStore:
    def __init__(self, postgres_url: str) -> None:
        try:
            import psycopg
        except ImportError as error:  # pragma: no cover
            raise RuntimeError(
                "PostgreSQL checkpointing requires the 'psycopg' package to be installed."
            ) from error

        self.postgres_url = postgres_url
        self._psycopg = psycopg
        self._ensure_schema()

    def save(self, workflow_id: str, label: str, state: WorkflowState) -> CheckpointRecord:
        record = CheckpointRecord(
            workflow_id=workflow_id,
            label=label,
            state=serialize_state(state),
        )
        with self._psycopg.connect(self.postgres_url) as connection:  # pragma: no cover
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO workflow_checkpoints (workflow_id, label, state_json, created_at)
                    VALUES (%s, %s, %s::jsonb, %s)
                    """,
                    (
                        record.workflow_id,
                        record.label,
                        json.dumps(record.state),
                        record.created_at.isoformat(),
                    ),
                )
            connection.commit()
        return record

    def load(self, workflow_id: str) -> list[CheckpointRecord]:
        with self._psycopg.connect(self.postgres_url) as connection:  # pragma: no cover
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT workflow_id, label, state_json::text, created_at
                    FROM workflow_checkpoints
                    WHERE workflow_id = %s
                    ORDER BY id ASC
                    """,
                    (workflow_id,),
                )
                rows = cursor.fetchall()
        return [
            CheckpointRecord(
                workflow_id=str(row[0]),
                label=str(row[1]),
                state=json.loads(str(row[2])),
                created_at=datetime.fromisoformat(str(row[3])),
            )
            for row in rows
        ]

    def get_path(self, workflow_id: str) -> str:
        parsed = urlparse(self.postgres_url)
        database = parsed.path.lstrip("/") or "postgres"
        return f"postgres://{parsed.hostname or 'localhost'}/{database}#{workflow_id}"

    def _ensure_schema(self) -> None:
        with self._psycopg.connect(self.postgres_url) as connection:  # pragma: no cover
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                        id BIGSERIAL PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        label TEXT NOT NULL,
                        state_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
            connection.commit()


def build_checkpoint_store(
    backend: str,
    *,
    checkpoint_dir: str | Path,
    postgres_url: str,
):
    normalized_backend = backend.strip().lower()
    if normalized_backend == "postgres":
        try:
            return PostgresCheckpointStore(postgres_url)
        except Exception:
            return SQLiteCheckpointStore(Path(checkpoint_dir) / "workflow_checkpoints.sqlite3")
    if normalized_backend == "sqlite":
        return SQLiteCheckpointStore(Path(checkpoint_dir) / "workflow_checkpoints.sqlite3")
    return JsonFileCheckpointStore(checkpoint_dir)
