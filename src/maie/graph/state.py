from __future__ import annotations

from dataclasses import is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict
from uuid import uuid4

from maie.domain.models import EscalationRecord, RiskAssessment, RoutingDecision, SupplierSignal


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    supplier_name: str
    sector: str
    jurisdiction: str
    signal_batch: list[SupplierSignal]
    research_notes: list[str]
    collected_evidence: list[str]
    risk_assessment: RiskAssessment | None
    draft_report: str | None
    routing_history: list[RoutingDecision]
    escalations: list[EscalationRecord]
    awaiting_human: bool
    human_decision: str | None
    status: str
    last_decision: RoutingDecision | None


def build_initial_state(
    supplier_name: str,
    signals: list[SupplierSignal],
    *,
    sector: str = "financial-services",
    jurisdiction: str = "US",
) -> WorkflowState:
    return WorkflowState(
        workflow_id=str(uuid4()),
        supplier_name=supplier_name,
        sector=sector,
        jurisdiction=jurisdiction,
        signal_batch=signals,
        research_notes=[],
        collected_evidence=[],
        risk_assessment=None,
        draft_report=None,
        routing_history=[],
        escalations=[],
        awaiting_human=False,
        human_decision=None,
        status="new",
        last_decision=None,
    )


def serialize_state(state: WorkflowState) -> dict[str, Any]:
    return {key: _serialize_value(value) for key, value in state.items()}


def _serialize_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if is_dataclass(value):
        if hasattr(value, "to_dict"):
            return value.to_dict()
        return {key: _serialize_value(item) for key, item in value.__dict__.items()}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value

