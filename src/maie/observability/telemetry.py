from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class TelemetryEvent:
    workflow_id: str
    event_name: str
    attributes: dict[str, Any]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "event_name": self.event_name,
            "attributes": self.attributes,
            "occurred_at": self.occurred_at.isoformat(),
        }


class WorkflowTelemetry:
    def __init__(self, *, enable_logging: bool = True) -> None:
        self.enable_logging = enable_logging
        self.events: list[TelemetryEvent] = []
        self._logger = logging.getLogger("maie.telemetry")

    def record(self, workflow_id: str, event_name: str, **attributes: Any) -> TelemetryEvent:
        event = TelemetryEvent(
            workflow_id=workflow_id,
            event_name=event_name,
            attributes=attributes,
        )
        self.events.append(event)
        if self.enable_logging:
            self._logger.info("%s %s", event_name, attributes)
        return event

    def summarize(self) -> dict[str, Any]:
        return {
            "event_count": len(self.events),
            "event_names": [event.event_name for event in self.events],
        }

