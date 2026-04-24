from __future__ import annotations

import json
import re
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

    def draft_scenario(self, prompt: str) -> dict[str, Any]:
        cleaned_prompt = " ".join(prompt.strip().split())
        if not cleaned_prompt:
            raise ValueError("Scenario prompt cannot be empty.")

        request = {
            "supplier_name": _infer_supplier_name(cleaned_prompt),
            "sector": _infer_sector(cleaned_prompt, self.settings.domain_context),
            "jurisdiction": _infer_jurisdiction(cleaned_prompt),
            "signals": _infer_signals(cleaned_prompt),
        }
        RiskWorkflowRequest.model_validate(request)
        return {
            "prompt": cleaned_prompt,
            "request": request,
            "signal_count": len(request["signals"]),
            "analysis": {
                "supplier_name": request["supplier_name"],
                "sector": request["sector"],
                "jurisdiction": request["jurisdiction"],
                "sources": [signal["source"] for signal in request["signals"]],
            },
        }

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


def _infer_supplier_name(prompt: str) -> str:
    patterns = [
        r"(?i)(?:supplier|vendor|manufacturer)\s+(?:named\s+)?([A-Z][A-Za-z0-9&\-]*(?:\s+[A-Z][A-Za-z0-9&\-]*){0,3})\s+(?:has|is|faces|reported|shows|disclosed|triggered)\b",
        r"\b([A-Z][A-Za-z0-9&\-]*(?:\s+[A-Z][A-Za-z0-9&\-]*){0,3})\s+(?:supplier|vendor|manufacturer)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return match.group(1).strip()
    return "Scenario Supplier"


def _infer_sector(prompt: str, default_sector: str) -> str:
    lowered = prompt.lower()
    if any(keyword in lowered for keyword in ["bank", "payments", "financial", "fintech", "treasury"]):
        return "financial-services"
    if any(keyword in lowered for keyword in ["hospital", "patient", "clinical", "healthcare"]):
        return "healthcare"
    if any(keyword in lowered for keyword in ["retail", "store", "e-commerce", "inventory"]):
        return "retail"
    return default_sector


def _infer_jurisdiction(prompt: str) -> str:
    lowered = prompt.lower()
    if any(keyword in lowered for keyword in ["united states", "u.s.", " us ", "usa"]):
        return "US"
    if "germany" in lowered or "berlin" in lowered or "munich" in lowered:
        return "DE"
    if "uk" in lowered or "united kingdom" in lowered or "london" in lowered:
        return "UK"
    if "europe" in lowered or "eu" in lowered:
        return "EU"
    if "singapore" in lowered:
        return "SG"
    return "US"


def _infer_signals(prompt: str) -> list[dict[str, Any]]:
    fragments = [
        fragment.strip(" -")
        for fragment in re.split(r"(?:[.;\n]+|\bwhile\b|\band\b|\bplus\b)", prompt, flags=re.IGNORECASE)
        if fragment.strip()
    ]
    signals: list[dict[str, Any]] = []

    for fragment in fragments:
        source = _infer_source(fragment)
        severity = _infer_severity(fragment)
        region = _infer_region(fragment)
        headline = _headline_from_fragment(fragment)
        summary = fragment if fragment.endswith(".") else f"{fragment}."
        signals.append(
            {
                "source": source,
                "headline": headline,
                "summary": summary,
                "severity": severity,
                "region": region,
            }
        )

    if not signals:
        signals.append(
            {
                "source": "news",
                "headline": "Scenario signal",
                "summary": prompt if prompt.endswith(".") else f"{prompt}.",
                "severity": 3,
                "region": "United States",
            }
        )

    return signals[:4]


def _infer_source(fragment: str) -> str:
    lowered = fragment.lower()
    if any(keyword in lowered for keyword in ["sec filing", "10-k", "10-q", "debt covenant", "earnings filing"]):
        return "sec_filing"
    if any(keyword in lowered for keyword in ["internal alert", "ticket", "war room", "monitoring", "sla breach"]):
        return "internal_alert"
    if any(keyword in lowered for keyword in ["supplier profile", "single-source", "tier-1", "vendor profile"]):
        return "supplier_profile"
    return "news"


def _infer_severity(fragment: str) -> int:
    lowered = fragment.lower()
    if any(keyword in lowered for keyword in ["critical", "material", "shutdown", "bankruptcy", "breach", "severe"]):
        return 5
    if any(keyword in lowered for keyword in ["major", "high risk", "debt covenant", "outage", "escalate", "liquidity"]):
        return 4
    if any(keyword in lowered for keyword in ["moderate", "delay", "watch", "disruption", "warning"]):
        return 3
    if any(keyword in lowered for keyword in ["minor", "temporary", "brief"]):
        return 2
    return 3


def _infer_region(fragment: str) -> str:
    lowered = fragment.lower()
    if "north america" in lowered:
        return "North America"
    if any(keyword in lowered for keyword in ["united states", "u.s.", "us ", "usa"]):
        return "United States"
    if any(keyword in lowered for keyword in ["europe", "germany", "uk", "united kingdom"]):
        return "Europe"
    if any(keyword in lowered for keyword in ["asia", "singapore", "japan", "india"]):
        return "APAC"
    return "United States"


def _headline_from_fragment(fragment: str) -> str:
    trimmed = fragment.strip()
    if len(trimmed) <= 72:
        return trimmed[:1].upper() + trimmed[1:]
    words = trimmed.split()
    headline = " ".join(words[:10])
    return f"{headline[:1].upper() + headline[1:]}..."
