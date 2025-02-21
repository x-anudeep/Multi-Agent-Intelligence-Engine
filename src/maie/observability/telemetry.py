from __future__ import annotations

import logging
from contextlib import nullcontext
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

try:
    from opentelemetry import trace
except ImportError:  # pragma: no cover
    trace = None


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
        self._tracer = trace.get_tracer("maie.workflow") if trace is not None else None

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

    def time_block(self, workflow_id: str, event_name: str, **attributes: Any):
        span_context = (
            self._tracer.start_as_current_span(event_name) if self._tracer is not None else nullcontext()
        )
        start = perf_counter()

        class TimedBlock:
            def __enter__(inner_self) -> Any:
                span = span_context.__enter__()
                if span is not None and hasattr(span, "set_attribute"):
                    span.set_attribute("workflow.id", workflow_id)
                    for key, value in attributes.items():
                        span.set_attribute(str(key), str(value))
                return span

            def __exit__(inner_self, exc_type, exc, traceback) -> None:
                duration_ms = round((perf_counter() - start) * 1000, 2)
                record_attributes = dict(attributes)
                record_attributes["duration_ms"] = duration_ms
                record_attributes["status"] = "error" if exc is not None else "ok"
                self.record(workflow_id, event_name, **record_attributes)
                span_context.__exit__(exc_type, exc, traceback)

        return TimedBlock()

    def summarize(self) -> dict[str, Any]:
        latencies = [
            float(event.attributes["duration_ms"])
            for event in self.events
            if "duration_ms" in event.attributes
        ]
        return {
            "event_count": len(self.events),
            "event_names": [event.event_name for event in self.events],
            "average_duration_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
            "max_duration_ms": round(max(latencies), 2) if latencies else 0.0,
        }
