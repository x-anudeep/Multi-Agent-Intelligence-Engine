from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from maie.domain.models import ProviderName, SignalSource, SupplierSignal


class SupplierSignalInput(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    source: SignalSource
    headline: str
    summary: str
    severity: int = Field(ge=1, le=5)
    region: str
    metadata: dict[str, str] = Field(default_factory=dict)
    supplier_name: str | None = None

    def to_domain(self, default_supplier_name: str) -> SupplierSignal:
        return SupplierSignal(
            supplier_name=self.supplier_name or default_supplier_name,
            source=self.source,
            headline=self.headline,
            summary=self.summary,
            severity=self.severity,
            region=self.region,
            metadata=self.metadata,
        )


class RiskWorkflowRequest(BaseModel):
    supplier_name: str
    sector: str = "financial-services"
    jurisdiction: str = "US"
    signals: list[SupplierSignalInput]
    max_steps: int = Field(default=8, ge=1, le=20)


class HealthResponse(BaseModel):
    service_name: str
    version: str
    environment: str
    status: str
    provider_mode: str
    governance_enabled: bool


class CheckpointResponse(BaseModel):
    label: str
    created_at: str
    state: dict[str, object]


class CheckpointHistoryResponse(BaseModel):
    workflow_id: str
    checkpoint_count: int
    checkpoints: list[CheckpointResponse]


class WorkflowExecutionResponse(BaseModel):
    workflow_id: str
    status: str
    checkpoint_count: int
    checkpoint_location: str | None
    telemetry_event_count: int
    routing_targets: list[str]
    tool_runs: int
    model_invocations: list[ProviderName]
    overall_risk_score: int | None
    disruption_probability: float | None
    requires_human_review: bool | None
    report_preview: str | None
    knowledge_hits: list[str]
    governance_approved: bool
    governance_findings: list[str]
    audit_trail: list[str]
    state_snapshot: dict[str, object]
