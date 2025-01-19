from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

