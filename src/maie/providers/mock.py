from __future__ import annotations

from typing import Any

from maie.domain.models import SignalSource
from maie.providers.base import BaseModelProvider, ModelOutput


class MockProvider(BaseModelProvider):
    async def generate_text(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        if task_name == "research_synthesis":
            supplier_name = str(context["supplier_name"])
            tool_results = list(context.get("tool_results", []))
            tool_summaries = [str(result["summary"]) for result in tool_results]
            content = (
                f"{supplier_name} shows converging disruption indicators across logistics, "
                f"regulatory, and supplier profile signals. Key findings: {'; '.join(tool_summaries)}"
            )
            return ModelOutput(
                provider=self.name,
                task_name=task_name,
                content=content,
                metadata={
                    "model_id": self.model_id,
                    "summary": "Mock provider generated a research synthesis from tool findings.",
                },
            )

        if task_name == "report_generation":
            supplier_name = str(context["supplier_name"])
            assessment = context.get("risk_assessment") or {}
            compliance_review = context.get("compliance_review") or {}
            recovery_actions = list(context.get("recovery_actions", []))
            actions = assessment.get("recommended_actions", [])
            content = "\n".join(
                [
                    f"# Supplier Risk Brief: {supplier_name}",
                    "",
                    f"Overall risk score: {assessment.get('overall_risk_score', 'n/a')}",
                    f"Disruption probability: {assessment.get('disruption_probability', 'n/a')}",
                    "",
                    "## Summary",
                    str(assessment.get("explanation", "No risk assessment available.")),
                    "",
                    "## Compliance",
                    str(compliance_review.get("summary", "No compliance review required.")),
                    "",
                    "## Recommended Actions",
                    *[f"- {action}" for action in actions],
                    "",
                    "## Recovery Plan",
                    *[f"- {action}" for action in recovery_actions],
                ]
            )
            return ModelOutput(
                provider=self.name,
                task_name=task_name,
                content=content,
                metadata={
                    "model_id": self.model_id,
                    "summary": "Mock provider rendered an executive-ready risk brief.",
                },
            )

        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content="Mock provider completed the text generation task.",
            metadata={"model_id": self.model_id},
        )

    async def generate_structured(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        if task_name == "compliance_review":
            signals = list(context.get("signals", []))
            risk_assessment = context.get("risk_assessment") or {}
            contains_sec_filing = any(signal["source"] == SignalSource.SEC_FILING.value for signal in signals)
            high_risk = int(risk_assessment.get("overall_risk_score", 0)) >= 80
            requires_human_signoff = contains_sec_filing or high_risk
            blocking_findings = []
            if contains_sec_filing:
                blocking_findings.append("Regulatory filing requires treasury and compliance signoff.")
            structured_content = {
                "status": "approved_with_controls" if not blocking_findings else "conditional_approval",
                "summary": (
                    "Compliance review validated disclosure, routing, and mitigation obligations."
                ),
                "obligations": [
                    "Notify risk operations when regulatory filings affect supplier continuity.",
                    "Document alternate supplier options for critical regions.",
                ],
                "mitigation_plan": [
                    "Activate alternate supplier shortlist within 24 hours.",
                    "Open treasury and procurement war room for high-risk suppliers.",
                    "Require daily checkpoint review until risk score drops below threshold.",
                ],
                "requires_human_signoff": requires_human_signoff,
                "blocking_findings": blocking_findings,
            }
            return ModelOutput(
                provider=self.name,
                task_name=task_name,
                content="Structured compliance review complete.",
                structured_content=structured_content,
                metadata={
                    "model_id": self.model_id,
                    "summary": "Mock provider returned a structured compliance review.",
                },
            )

        if task_name != "risk_assessment":
            return ModelOutput(
                provider=self.name,
                task_name=task_name,
                content="Unsupported structured task.",
                structured_content={},
                metadata={"model_id": self.model_id},
            )

        signals = list(context.get("signals", []))
        if not signals:
            average_severity = 1.0
            contains_sec_filing = False
            high_severity_count = 0
        else:
            average_severity = sum(int(signal["severity"]) for signal in signals) / len(signals)
            contains_sec_filing = any(signal["source"] == SignalSource.SEC_FILING.value for signal in signals)
            high_severity_count = sum(1 for signal in signals if int(signal["severity"]) >= 4)

        score = min(int((average_severity * 18) + (high_severity_count * 6) + (10 if contains_sec_filing else 0)), 100)
        probability = round(min((average_severity / 5) + (0.1 if contains_sec_filing else 0), 1.0), 2)
        requires_human_review = contains_sec_filing or score >= 80
        explanation = (
            f"Model assessed {high_severity_count} high-severity signals with "
            f"{'regulatory exposure' if contains_sec_filing else 'no direct regulatory filing risk'}."
        )
        structured_content = {
            "overall_risk_score": score,
            "disruption_probability": probability,
            "explanation": explanation,
            "recommended_actions": [
                "Validate alternate supplier capacity for exposed regions.",
                "Notify procurement leadership when disruption probability crosses policy thresholds.",
                "Escalate all regulatory or balance-sheet stress indicators for analyst review.",
            ],
            "requires_human_review": requires_human_review,
        }
        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content="Structured assessment complete.",
            structured_content=structured_content,
            metadata={
                "model_id": self.model_id,
                "summary": "Mock provider returned a structured risk assessment.",
            },
        )
