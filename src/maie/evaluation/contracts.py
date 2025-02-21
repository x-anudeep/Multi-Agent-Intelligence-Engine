from __future__ import annotations

from pydantic import BaseModel, Field

from maie.api.contracts import RiskWorkflowRequest


class EvaluationExpectation(BaseModel):
    expected_status: str = "complete"
    expected_requires_human_review: bool | None = None
    expected_min_risk_score: int | None = None
    expected_max_risk_score: int | None = None
    required_route_targets: list[str] = Field(default_factory=list)


class EvaluationCase(BaseModel):
    case_id: str
    description: str
    request: RiskWorkflowRequest
    expectation: EvaluationExpectation


class EvaluationCaseResult(BaseModel):
    case_id: str
    passed: bool
    status_match: bool
    risk_score_match: bool
    human_review_match: bool
    route_match: bool
    observed_risk_score: int | None
    observed_requires_human_review: bool | None
    reasons: list[str] = Field(default_factory=list)


class EvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    pass_rate: float
    average_observed_risk_score: float
    results: list[EvaluationCaseResult]


class BenchmarkCaseResult(BaseModel):
    case_id: str
    passed: bool
    latency_ms: float
    checkpoint_count: int
    snapshot_count: int
    routing_branch_count: int
    telemetry_event_count: int


class BenchmarkSummary(BaseModel):
    total_cases: int
    pass_rate: float
    average_latency_ms: float
    p95_latency_ms: float
    total_checkpoints: int
    total_snapshots: int
    total_telemetry_events: int
    max_routing_branch_count: int
    results: list[BenchmarkCaseResult]
