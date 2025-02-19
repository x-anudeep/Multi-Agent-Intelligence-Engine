from __future__ import annotations

from dataclasses import is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict
from uuid import uuid4

from maie.domain.models import (
    ComplianceReview,
    EscalationRecord,
    ModelInvocationRecord,
    RiskAssessment,
    RoutingDecision,
    SupplierSignal,
    ToolExecutionRecord,
)


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    supplier_name: str
    sector: str
    jurisdiction: str
    signal_batch: list[SupplierSignal]
    research_notes: list[str]
    collected_evidence: list[str]
    risk_assessment: RiskAssessment | None
    compliance_review: ComplianceReview | None
    draft_report: str | None
    routing_history: list[RoutingDecision]
    escalations: list[EscalationRecord]
    tool_history: list[ToolExecutionRecord]
    model_history: list[ModelInvocationRecord]
    knowledge_hits: list[str]
    audit_trail: list[str]
    checkpoint_labels: list[str]
    snapshot_labels: list[str]
    awaiting_human: bool
    human_decision: str | None
    human_review_required: bool
    compliance_required: bool
    compliance_blocked: bool
    recovery_actions: list[str]
    routing_branch_count: int
    snapshot_count: int
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
        compliance_review=None,
        draft_report=None,
        routing_history=[],
        escalations=[],
        tool_history=[],
        model_history=[],
        knowledge_hits=[],
        audit_trail=[],
        checkpoint_labels=[],
        snapshot_labels=[],
        awaiting_human=False,
        human_decision=None,
        human_review_required=False,
        compliance_required=False,
        compliance_blocked=False,
        recovery_actions=[],
        routing_branch_count=0,
        snapshot_count=0,
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
