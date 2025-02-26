from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from maie.api.contracts import RiskWorkflowRequest
from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings


class LiveDemoService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.workflow_service = WorkflowApplicationService(settings)

    def health_payload(self) -> dict[str, Any]:
        health = self.workflow_service.health().model_dump(mode="json")
        health["demo_mode"] = "live-demo"
        health["scenarios_available"] = len(self.list_scenarios())
        return health

    def list_scenarios(self) -> list[dict[str, Any]]:
        return _load_demo_scenarios()["scenarios"]

    async def run_workflow(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = RiskWorkflowRequest.model_validate(payload)
        response = await self.workflow_service.execute_risk_workflow(request)
        checkpoints = self.workflow_service.get_checkpoint_history(response.workflow_id)
        state = response.state_snapshot
        return {
            "workflow": response.model_dump(mode="json"),
            "checkpoints": checkpoints.model_dump(mode="json"),
            "dashboard": {
                "supplier_name": request.supplier_name,
                "sector": request.sector,
                "jurisdiction": request.jurisdiction,
                "workflow_status": response.status,
                "risk_score": response.overall_risk_score,
                "disruption_probability": response.disruption_probability,
                "requires_human_review": response.requires_human_review,
                "checkpoint_count": response.checkpoint_count,
                "snapshot_count": response.snapshot_count,
                "checkpoint_location": response.checkpoint_location,
                "telemetry_event_count": response.telemetry_event_count,
                "average_event_duration_ms": response.average_event_duration_ms,
                "routing_branch_count": response.routing_branch_count,
                "tool_runs": response.tool_runs,
                "routing_targets": response.routing_targets,
                "model_invocations": [provider.value for provider in response.model_invocations],
                "governance_findings": response.governance_findings,
                "governance_approved": response.governance_approved,
                "knowledge_hits": response.knowledge_hits,
                "report_preview": response.report_preview,
                "audit_trail": response.audit_trail,
                "checkpoint_labels": state.get("checkpoint_labels", []),
                "snapshot_labels": state.get("snapshot_labels", []),
                "compliance_review": state.get("compliance_review"),
                "recovery_actions": state.get("recovery_actions", []),
                "human_decision": state.get("human_decision"),
            },
        }


def _load_demo_scenarios() -> dict[str, Any]:
    resource = files("maie.demo").joinpath("data", "scenarios.json")
    return json.loads(resource.read_text(encoding="utf-8"))
