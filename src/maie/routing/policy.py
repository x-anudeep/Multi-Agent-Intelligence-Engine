from __future__ import annotations

from maie.domain.models import AgentTarget, ProviderName, RoutingDecision
from maie.graph.state import WorkflowState


class PolicyRouter:
    """Enterprise policy router with multi-branch workflow control."""

    def route(self, state: WorkflowState) -> RoutingDecision:
        if state.get("awaiting_human"):
            return RoutingDecision(
                target_agent=AgentTarget.HUMAN_REVIEW,
                provider=ProviderName.NONE,
                reason="Workflow is paused pending human review.",
            )

        if state.get("human_decision") == "rejected":
            return RoutingDecision(
                target_agent=AgentTarget.HUMAN_REVIEW,
                provider=ProviderName.NONE,
                reason="Human review rejected the current workflow outcome.",
            )

        if not state.get("research_notes"):
            return RoutingDecision(
                target_agent=AgentTarget.RESEARCH,
                provider=ProviderName.ANTHROPIC,
                reason="No research evidence exists yet, so gather context first.",
            )

        if not state.get("collected_evidence"):
            return RoutingDecision(
                target_agent=AgentTarget.RESEARCH,
                provider=ProviderName.ANTHROPIC,
                reason="Research completed without evidence, so gather more source data.",
            )

        assessment = state.get("risk_assessment")
        if assessment is None:
            return RoutingDecision(
                target_agent=AgentTarget.RISK_SCORING,
                provider=ProviderName.VERTEX_AI,
                reason="Research is complete and the workflow needs a structured risk score.",
            )

        if assessment.requires_human_review and state.get("human_decision") != "approved_for_reporting":
            return RoutingDecision(
                target_agent=AgentTarget.HUMAN_REVIEW,
                provider=ProviderName.NONE,
                reason="Risk policy triggered human escalation.",
            )

        if state.get("compliance_blocked"):
            return RoutingDecision(
                target_agent=AgentTarget.HUMAN_REVIEW,
                provider=ProviderName.NONE,
                reason="Compliance review found blocking issues that require human signoff.",
            )

        compliance_review = state.get("compliance_review")
        if compliance_review is None:
            return RoutingDecision(
                target_agent=AgentTarget.COMPLIANCE_REVIEW,
                provider=ProviderName.OPENAI,
                reason="Every risk assessment requires a compliance review before reporting.",
            )

        if (
            assessment.overall_risk_score >= 85
            and not state.get("recovery_actions")
            and compliance_review is not None
        ):
            return RoutingDecision(
                target_agent=AgentTarget.COMPLIANCE_REVIEW,
                provider=ProviderName.OPENAI,
                reason="High-risk outcomes require a mitigation plan before final reporting.",
            )

        if state.get("human_review_required") and state.get("human_decision") != "approved_for_reporting":
            return RoutingDecision(
                target_agent=AgentTarget.HUMAN_REVIEW,
                provider=ProviderName.NONE,
                reason="Workflow still requires explicit human approval.",
            )

        if not state.get("draft_report"):
            return RoutingDecision(
                target_agent=AgentTarget.REPORT,
                provider=ProviderName.OPENAI,
                reason="Risk score exists, so generate the analyst-facing report.",
            )

        return RoutingDecision(
            target_agent=AgentTarget.FINISH,
            provider=ProviderName.NONE,
            reason="Workflow has all required outputs.",
        )
