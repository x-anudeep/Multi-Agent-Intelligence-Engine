from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class SignalSource(StrEnum):
    NEWS = "news"
    SEC_FILING = "sec_filing"
    SUPPLIER_PROFILE = "supplier_profile"
    INTERNAL_ALERT = "internal_alert"


class ProviderName(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    VERTEX_AI = "vertex_ai"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    NONE = "none"


class AgentTarget(StrEnum):
    RESEARCH = "research_agent"
    RISK_SCORING = "risk_scoring_agent"
    COMPLIANCE_REVIEW = "compliance_review_agent"
    REPORT = "report_generation_agent"
    HUMAN_REVIEW = "human_review_agent"
    FINISH = "finish"


class WorkflowStatus(StrEnum):
    NEW = "new"
    RESEARCHING = "researching"
    SCORING = "scoring"
    COMPLIANCE_REVIEW = "compliance_review"
    REPORTING = "reporting"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETE = "complete"
    BLOCKED = "blocked"


@dataclass(slots=True)
class SupplierSignal:
    supplier_name: str
    source: SignalSource
    headline: str
    summary: str
    severity: int
    region: str
    published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["published_at"] = self.published_at.isoformat()
        payload["source"] = self.source.value
        return payload


@dataclass(slots=True)
class RiskAssessment:
    supplier_name: str
    overall_risk_score: int
    disruption_probability: float
    explanation: str
    evidence: list[str]
    recommended_actions: list[str]
    requires_human_review: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class EscalationRecord:
    reason: str
    severity_band: str
    owner_team: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["created_at"] = self.created_at.isoformat()
        return payload


@dataclass(slots=True)
class RoutingDecision:
    target_agent: AgentTarget
    provider: ProviderName
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "target_agent": self.target_agent.value,
            "provider": self.provider.value,
            "reason": self.reason,
        }


@dataclass(slots=True)
class ToolExecutionRecord:
    tool_name: str
    status: str
    summary: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class ModelInvocationRecord:
    provider: ProviderName
    task_name: str
    summary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "provider": self.provider.value,
            "task_name": self.task_name,
            "summary": self.summary,
        }


@dataclass(slots=True)
class ComplianceReview:
    status: str
    summary: str
    obligations: list[str]
    mitigation_plan: list[str]
    requires_human_signoff: bool
    blocking_findings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
