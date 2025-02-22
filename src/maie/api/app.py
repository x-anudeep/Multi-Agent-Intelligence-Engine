from __future__ import annotations

from maie.api.contracts import (
    CheckpointHistoryResponse,
    HealthResponse,
    RiskWorkflowRequest,
    WorkflowExecutionResponse,
)
from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings


def fastapi_available() -> bool:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return False
    return True


def create_app(
    *,
    settings: Settings | None = None,
    service: WorkflowApplicationService | None = None,
):
    try:
        from fastapi import FastAPI, HTTPException
    except ImportError as error:  # pragma: no cover
        raise RuntimeError(
            "FastAPI is not installed. Install project dependencies to run the HTTP service."
        ) from error

    resolved_settings = settings or Settings.from_env()
    workflow_service = service or WorkflowApplicationService(resolved_settings)

    app = FastAPI(
        title="Multi-Agent Intelligence Engine",
        version=resolved_settings.app_version,
        description=(
            "Enterprise supply chain risk workflow service with routing, "
            "snapshots, relational checkpointing, and runtime telemetry metrics."
        ),
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return workflow_service.health()

    @app.post(
        "/v1/workflows/risk-assessment",
        response_model=WorkflowExecutionResponse,
    )
    async def execute_workflow(
        request: RiskWorkflowRequest,
    ) -> WorkflowExecutionResponse:
        return await workflow_service.execute_risk_workflow(request)

    @app.get(
        "/v1/workflows/{workflow_id}/checkpoints",
        response_model=CheckpointHistoryResponse,
    )
    async def checkpoint_history(workflow_id: str) -> CheckpointHistoryResponse:
        response = workflow_service.get_checkpoint_history(workflow_id)
        if not response.checkpoints:
            raise HTTPException(status_code=404, detail="Workflow checkpoints not found.")
        return response

    return app
