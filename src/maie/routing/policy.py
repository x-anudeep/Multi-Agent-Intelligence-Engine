from __future__ import annotations

from maie.domain.models import AgentTarget, ProviderName, RoutingDecision
from maie.graph.state import WorkflowState


class PolicyRouter:
    """Simple enterprise-style policy router for deterministic workflow control."""

    def route(self, state: WorkflowState) -> RoutingDecision:
        if state.get("awaiting_human"):
            return RoutingDecision(
                target_agent=AgentTarget.HUMAN_REVIEW,
                provider=ProviderName.NONE,
                reason="Workflow is paused pending human review.",
            )

        if not state.get("research_notes"):
            return RoutingDecision(
                target_agent=AgentTarget.RESEARCH,
                provider=ProviderName.ANTHROPIC,
                reason="No research evidence exists yet, so gather context first.",
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
