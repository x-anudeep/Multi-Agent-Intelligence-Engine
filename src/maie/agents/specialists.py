from __future__ import annotations

from maie.agents.base import AgentExecutionResult, BaseAgent
from maie.domain.models import (
    AgentTarget,
    ComplianceReview,
    EscalationRecord,
    ModelInvocationRecord,
    ProviderName,
    RiskAssessment,
    ToolExecutionRecord,
    WorkflowStatus,
)
from maie.graph.state import WorkflowState


class ResearchAgent(BaseAgent):
    name = AgentTarget.RESEARCH
    provider = ProviderName.ANTHROPIC

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        signals = state.get("signal_batch", [])
        tool_registry = self.tool_registry
        tool_results: list[dict[str, object]] = []
        tool_history = [*state.get("tool_history", [])]
        knowledge_hits = [*state.get("knowledge_hits", [])]

        if tool_registry is not None:
            for tool_name in [
                "news_search",
                "sec_filings_lookup",
                "supplier_profile_lookup",
                "regional_exposure_map",
            ]:
                result = tool_registry.invoke(
                    tool_name,
                    supplier_name=state["supplier_name"],
                    signals=signals,
                )
                tool_results.append(result)
                tool_history.append(
                    ToolExecutionRecord(
                        tool_name=tool_name,
                        status="success",
                        summary=str(result["summary"]),
                    )
                )

        if self.knowledge_retriever is not None:
            query = " ".join(
                [
                    state["supplier_name"],
                    *[signal.headline for signal in signals],
                ]
            )
            retrievals = self.knowledge_retriever.retrieve(query, top_k=2)
            knowledge_hits.extend(
                [f"{hit.title}: {hit.excerpt}" for hit in retrievals]
            )

        provider = self._require_provider_registry().get(self.provider)
        provider_output = await provider.generate_text(
            "research_synthesis",
            {
                "supplier_name": state["supplier_name"],
                "signals": [signal.to_dict() for signal in signals],
                "tool_results": tool_results,
                "knowledge_hits": knowledge_hits,
            },
        )

        notes = [
            provider_output.content,
            *[
                f"{signal.source.value}: {signal.headline} | severity={signal.severity} | region={signal.region}"
                for signal in signals
            ],
        ]
        evidence = [finding for result in tool_results for finding in result.get("findings", [])]
        evidence.extend(knowledge_hits)
        if not evidence:
            evidence = [
                f"Evidence extracted from {signal.source.value}: {signal.summary}"
                for signal in signals
            ]

        model_history = [
            *state.get("model_history", []),
            ModelInvocationRecord(
                provider=self.provider,
                task_name="research_synthesis",
                summary=str(
                    provider_output.metadata.get(
                    "summary",
                    "Research provider synthesized multi-tool evidence.",
                    )
                ),
            ),
        ]
        audit_trail = [
            *state.get("audit_trail", []),
            "Research agent synthesized source-level evidence into normalized notes.",
        ]
        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "research_notes": notes,
                "collected_evidence": evidence,
                "tool_history": tool_history,
                "model_history": model_history,
                "knowledge_hits": knowledge_hits,
                "audit_trail": audit_trail,
                "status": WorkflowStatus.RESEARCHING.value,
            },
            audit_log="Research agent synthesized source-level evidence into normalized notes.",
        )


class RiskScoringAgent(BaseAgent):
    name = AgentTarget.RISK_SCORING
    provider = ProviderName.VERTEX_AI

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        signals = state.get("signal_batch", [])
        provider = self._require_provider_registry().get(self.provider)
        provider_output = await provider.generate_structured(
            "risk_assessment",
            {
                "supplier_name": state["supplier_name"],
                "signals": [signal.to_dict() for signal in signals],
                "evidence": state.get("collected_evidence", []),
            },
        )
        assessment_payload = provider_output.structured_content
        requires_human_review = bool(assessment_payload["requires_human_review"])

        assessment = RiskAssessment(
            supplier_name=state["supplier_name"],
            overall_risk_score=int(assessment_payload["overall_risk_score"]),
            disruption_probability=float(assessment_payload["disruption_probability"]),
            explanation=str(assessment_payload["explanation"]),
            evidence=state.get("collected_evidence", []),
            recommended_actions=list(assessment_payload["recommended_actions"]),
            requires_human_review=requires_human_review,
        )
        model_history = [
            *state.get("model_history", []),
            ModelInvocationRecord(
                provider=self.provider,
                task_name="risk_assessment",
                summary=str(
                    provider_output.metadata.get(
                    "summary",
                    "Risk scoring provider returned a structured assessment.",
                    )
                ),
            ),
        ]
        audit_trail = [
            *state.get("audit_trail", []),
            "Risk scoring agent calculated disruption risk and escalation status.",
        ]
        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "risk_assessment": assessment,
                "awaiting_human": requires_human_review,
                "human_review_required": requires_human_review,
                "compliance_required": (
                    requires_human_review
                    or any(signal.source.value == "sec_filing" for signal in signals)
                ),
                "model_history": model_history,
                "audit_trail": audit_trail,
                "status": (
                    WorkflowStatus.WAITING_FOR_HUMAN.value
                    if requires_human_review
                    else WorkflowStatus.SCORING.value
                ),
            },
            audit_log="Risk scoring agent calculated disruption risk and escalation status.",
        )


class ComplianceReviewAgent(BaseAgent):
    name = AgentTarget.COMPLIANCE_REVIEW
    provider = ProviderName.OPENAI

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        provider = self._require_provider_registry().get(self.provider)
        assessment = state.get("risk_assessment")
        provider_output = await provider.generate_structured(
            "compliance_review",
            {
                "supplier_name": state["supplier_name"],
                "jurisdiction": state["jurisdiction"],
                "signals": [signal.to_dict() for signal in state.get("signal_batch", [])],
                "risk_assessment": assessment.to_dict() if assessment else None,
                "evidence": state.get("collected_evidence", []),
            },
        )
        review_payload = provider_output.structured_content
        review = ComplianceReview(
            status=str(review_payload["status"]),
            summary=str(review_payload["summary"]),
            obligations=list(review_payload["obligations"]),
            mitigation_plan=list(review_payload["mitigation_plan"]),
            requires_human_signoff=bool(review_payload["requires_human_signoff"]),
            blocking_findings=list(review_payload["blocking_findings"]),
        )
        model_history = [
            *state.get("model_history", []),
            ModelInvocationRecord(
                provider=self.provider,
                task_name="compliance_review",
                summary=str(
                    provider_output.metadata.get(
                        "summary",
                        "Compliance provider validated escalation and mitigation obligations.",
                    )
                ),
            ),
        ]
        audit_trail = [
            *state.get("audit_trail", []),
            "Compliance review agent validated obligations and mitigation actions.",
        ]
        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "compliance_review": review,
                "compliance_required": True,
                "compliance_blocked": bool(review.blocking_findings),
                "awaiting_human": bool(review.requires_human_signoff),
                "human_review_required": bool(review.requires_human_signoff),
                "recovery_actions": review.mitigation_plan,
                "model_history": model_history,
                "audit_trail": audit_trail,
                "status": (
                    WorkflowStatus.WAITING_FOR_HUMAN.value
                    if review.requires_human_signoff
                    else WorkflowStatus.COMPLIANCE_REVIEW.value
                ),
            },
            audit_log="Compliance review agent validated obligations and mitigation actions.",
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
                "human_review_required": False,
                "compliance_blocked": False,
                "audit_trail": [
                    *state.get("audit_trail", []),
                    "Human review agent recorded an escalation and approved downstream reporting.",
                ],
                "status": WorkflowStatus.SCORING.value,
            },
            audit_log="Human review agent recorded an escalation and approved downstream reporting.",
        )


class ReportGenerationAgent(BaseAgent):
    name = AgentTarget.REPORT
    provider = ProviderName.OPENAI

    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        assessment = state.get("risk_assessment")
        compliance_review = state.get("compliance_review")
        provider = self._require_provider_registry().get(self.provider)
        provider_output = await provider.generate_text(
            "report_generation",
            {
                "supplier_name": state["supplier_name"],
                "risk_assessment": assessment.to_dict() if assessment else None,
                "compliance_review": compliance_review.to_dict() if compliance_review else None,
                "research_notes": state.get("research_notes", []),
                "escalations": [item.to_dict() for item in state.get("escalations", [])],
                "recovery_actions": state.get("recovery_actions", []),
            },
        )
        report = provider_output.content

        return AgentExecutionResult(
            agent_name=self.name,
            state_updates={
                "draft_report": report,
                "model_history": [
                    *state.get("model_history", []),
                    ModelInvocationRecord(
                        provider=self.provider,
                        task_name="report_generation",
                        summary=str(
                            provider_output.metadata.get(
                            "summary",
                            "Report provider produced an analyst-facing brief.",
                            )
                        ),
                    ),
                ],
                "audit_trail": [
                    *state.get("audit_trail", []),
                    "Report generation agent created the first analyst-ready output.",
                ],
                "status": WorkflowStatus.REPORTING.value,
            },
            audit_log="Report generation agent created the first analyst-ready output.",
        )
