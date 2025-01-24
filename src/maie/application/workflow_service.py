from __future__ import annotations

from collections.abc import Callable

from maie.api.contracts import (
    CheckpointHistoryResponse,
    CheckpointResponse,
    HealthResponse,
    RiskWorkflowRequest,
    WorkflowExecutionResponse,
)
from maie.core.config import Settings
from maie.graph.state import serialize_state
from maie.runtime.engine import WorkflowEngine, WorkflowRunArtifacts, build_default_engine


class WorkflowApplicationService:
    def __init__(
        self,
        settings: Settings,
        *,
        engine_factory: Callable[[Settings], WorkflowEngine] = build_default_engine,
    ) -> None:
        self.settings = settings
        self.engine_factory = engine_factory

    async def execute_risk_workflow(
        self,
        request: RiskWorkflowRequest,
    ) -> WorkflowExecutionResponse:
        engine = self.engine_factory(self.settings)
        artifacts = await engine.run(
            request.supplier_name,
            [signal.to_domain(request.supplier_name) for signal in request.signals],
            sector=request.sector,
            jurisdiction=request.jurisdiction,
            max_steps=request.max_steps,
        )
        return self._build_execution_response(artifacts)

    def get_checkpoint_history(self, workflow_id: str) -> CheckpointHistoryResponse:
        engine = self.engine_factory(self.settings)
        records = engine.load_checkpoints(workflow_id)
        checkpoints = [
            CheckpointResponse(
                label=record.label,
                created_at=record.created_at.isoformat(),
                state=record.state,
            )
            for record in records
        ]
        return CheckpointHistoryResponse(
            workflow_id=workflow_id,
            checkpoint_count=len(checkpoints),
            checkpoints=checkpoints,
        )

    def health(self) -> HealthResponse:
        return HealthResponse(
            service_name=self.settings.app_name,
            version=self.settings.app_version,
            environment=self.settings.environment,
            status="ok",
            provider_mode="mock" if self.settings.use_mock_providers else "live",
        )

    def _build_execution_response(
        self,
        artifacts: WorkflowRunArtifacts,
    ) -> WorkflowExecutionResponse:
        state = artifacts.state
        risk_assessment = state.get("risk_assessment")
        return WorkflowExecutionResponse(
            workflow_id=state["workflow_id"],
            status=state["status"],
            checkpoint_count=len(artifacts.checkpoint_records),
            checkpoint_location=artifacts.checkpoint_location,
            telemetry_event_count=artifacts.telemetry.summarize()["event_count"],
            routing_targets=[
                decision.target_agent.value for decision in state.get("routing_history", [])
            ],
            tool_runs=len(state.get("tool_history", [])),
            model_invocations=[
                record.provider for record in state.get("model_history", [])
            ],
            overall_risk_score=(
                risk_assessment.overall_risk_score if risk_assessment is not None else None
            ),
            disruption_probability=(
                risk_assessment.disruption_probability if risk_assessment is not None else None
            ),
            requires_human_review=(
                risk_assessment.requires_human_review if risk_assessment is not None else None
            ),
            report_preview=state.get("draft_report"),
            audit_trail=state.get("audit_trail", []),
            state_snapshot=serialize_state(state),
        )
