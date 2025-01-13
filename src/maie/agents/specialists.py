from __future__ import annotations

from maie.agents.base import AgentExecutionResult, BaseAgent
from maie.domain.models import (
    AgentTarget,
    EscalationRecord,
    ProviderName,
    RiskAssessment,
    SignalSource,
    WorkflowStatus,
)
from maie.graph.state import WorkflowState


class ResearchAgent(BaseAgent):
    name = AgentTarget.RESEARCH
    provider = ProviderName.ANTHROPIC

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        signals = state.get("signal_batch", [])
        notes = [
            f"{signal.source.value}: {signal.headline} | severity={signal.severity} | region={signal.region}"
            for signal in signals
        ]
        evidence = [
            f"Evidence extracted from {signal.source.value}: {signal.summary}"
            for signal in signals
        ]
        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "research_notes": notes,
                "collected_evidence": evidence,
                "status": WorkflowStatus.RESEARCHING.value,
            },
            audit_log="Research agent synthesized source-level evidence into normalized notes.",
        )


class RiskScoringAgent(BaseAgent):
    name = AgentTarget.RISK_SCORING
    provider = ProviderName.VERTEX_AI

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        signals = state.get("signal_batch", [])
        if not signals:
            average_severity = 1
            contains_sec_filing = False
        else:
            average_severity = sum(signal.severity for signal in signals) / len(signals)
            contains_sec_filing = any(signal.source == SignalSource.SEC_FILING for signal in signals)

        risk_score = min(int(average_severity * 20), 100)
        disruption_probability = round(min(average_severity / 5, 1.0), 2)
        requires_human_review = contains_sec_filing or risk_score >= 80

        assessment = RiskAssessment(
            supplier_name=state["supplier_name"],
            overall_risk_score=risk_score,
            disruption_probability=disruption_probability,
            explanation=(
                "Risk score is based on signal severity, source mix, and regulatory presence."
            ),
            evidence=state.get("collected_evidence", []),
            recommended_actions=[
                "Review alternate suppliers for high-exposure regions.",
                "Alert procurement leadership if disruption probability exceeds threshold.",
                "Escalate any regulatory signal for analyst confirmation.",
            ],
            requires_human_review=requires_human_review,
        )
        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "risk_assessment": assessment,
                "awaiting_human": requires_human_review,
                "status": (
                    WorkflowStatus.WAITING_FOR_HUMAN.value
                    if requires_human_review
                    else WorkflowStatus.SCORING.value
                ),
            },
            audit_log="Risk scoring agent calculated disruption risk and escalation status.",
        )


class HumanReviewAgent(BaseAgent):
    name = AgentTarget.HUMAN_REVIEW
    provider = ProviderName.NONE

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        assessment = state.get("risk_assessment")
        reason = "Human review required by risk policy."
        severity_band = "high" if assessment and assessment.overall_risk_score >= 80 else "medium"
        escalations = [
            *state.get("escalations", []),
            EscalationRecord(
                reason=reason,
                severity_band=severity_band,
                owner_team="supply-chain-risk-ops",
            ),
        ]
        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "escalations": escalations,
                "awaiting_human": False,
                "human_decision": "approved_for_reporting",
                "status": WorkflowStatus.WAITING_FOR_HUMAN.value,
            },
            audit_log="Human review agent recorded an escalation and approved downstream reporting.",
        )


class ReportGenerationAgent(BaseAgent):
    name = AgentTarget.REPORT
    provider = ProviderName.OPENAI

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        assessment = state.get("risk_assessment")
        if assessment is None:
            report = "Risk assessment unavailable."
        else:
            report = "\n".join(
                [
                    f"# Supplier Risk Brief: {assessment.supplier_name}",
                    "",
                    f"Overall risk score: {assessment.overall_risk_score}",
                    f"Disruption probability: {assessment.disruption_probability}",
                    "",
                    "## Summary",
                    assessment.explanation,
                    "",
                    "## Recommended Actions",
                    *[f"- {action}" for action in assessment.recommended_actions],
                ]
            )

        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "draft_report": report,
                "status": WorkflowStatus.REPORTING.value,
            },
            audit_log="Report generation agent created the first analyst-ready output.",
        )

