from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from maie.graph.state import WorkflowState, serialize_state

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


@dataclass(slots=True)
class SnapshotRecord:
    workflow_id: str
    label: str
    state: dict[str, object]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, object]:
        return {
            "workflow_id": self.workflow_id,
            "label": self.label,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
        }


class RuntimeStateStore(Protocol):
    def save_snapshot(self, workflow_id: str, label: str, state: WorkflowState) -> SnapshotRecord:
        ...

    def load_snapshots(self, workflow_id: str) -> list[SnapshotRecord]:
        ...


class InMemoryRuntimeStateStore:
    def __init__(self) -> None:
        self._snapshots: dict[str, list[SnapshotRecord]] = {}

    def save_snapshot(self, workflow_id: str, label: str, state: WorkflowState) -> SnapshotRecord:
        record = SnapshotRecord(
            workflow_id=workflow_id,
            label=label,
            state=serialize_state(state),
        )
        self._snapshots.setdefault(workflow_id, []).append(record)
        return record

    def load_snapshots(self, workflow_id: str) -> list[SnapshotRecord]:
        return list(self._snapshots.get(workflow_id, []))


class RedisRuntimeStateStore:
    def __init__(self, redis_url: str) -> None:
        if redis is None:  # pragma: no cover
            raise RuntimeError("Redis snapshot persistence requires the 'redis' package.")
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def save_snapshot(self, workflow_id: str, label: str, state: WorkflowState) -> SnapshotRecord:
        record = SnapshotRecord(
            workflow_id=workflow_id,
            label=label,
            state=serialize_state(state),
        )
        self.client.rpush(self._key(workflow_id), json.dumps(record.to_dict()))
        return record

    def load_snapshots(self, workflow_id: str) -> list[SnapshotRecord]:
        payloads = self.client.lrange(self._key(workflow_id), 0, -1)
        snapshots: list[SnapshotRecord] = []
        for payload in payloads:
            decoded = json.loads(payload)
            snapshots.append(
                SnapshotRecord(
                    workflow_id=str(decoded["workflow_id"]),
                    label=str(decoded["label"]),
                    state=dict(decoded["state"]),
                    created_at=datetime.fromisoformat(str(decoded["created_at"])),
                )
            )
        return snapshots

    @staticmethod
    def _key(workflow_id: str) -> str:
        return f"maie:workflow:{workflow_id}:snapshots"


def build_runtime_state_store(state_backend: str, redis_url: str) -> RuntimeStateStore:
    if state_backend.strip().lower() == "redis":
        try:
            return RedisRuntimeStateStore(redis_url)
        except Exception:
            return InMemoryRuntimeStateStore()
    return InMemoryRuntimeStateStore()
