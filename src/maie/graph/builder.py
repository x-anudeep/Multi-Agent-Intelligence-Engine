from __future__ import annotations

from collections.abc import Callable
from typing import Any

from maie.agents.base import BaseAgent
from maie.agents.specialists import (
    ComplianceReviewAgent,
    HumanReviewAgent,
    ReportGenerationAgent,
    ResearchAgent,
    RiskScoringAgent,
)
from maie.core.config import Settings
from maie.domain.models import AgentTarget
from maie.graph.state import WorkflowState
from maie.providers.registry import build_default_provider_registry
from maie.routing.policy import PolicyRouter
from maie.tools.intelligence import build_default_tool_registry

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:  # pragma: no cover
    END = "__end__"
    START = "__start__"
    StateGraph = None


def build_graph() -> Any:
    if StateGraph is None:
        raise RuntimeError(
            "LangGraph is not installed. Install project dependencies to compile the workflow graph."
        )

    router = PolicyRouter()
    settings = Settings()
    provider_registry = build_default_provider_registry(settings)
    tool_registry = build_default_tool_registry()
    agents: dict[AgentTarget, BaseAgent] = {
        AgentTarget.RESEARCH: ResearchAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
        ),
        AgentTarget.RISK_SCORING: RiskScoringAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
        ),
        AgentTarget.COMPLIANCE_REVIEW: ComplianceReviewAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
        ),
        AgentTarget.REPORT: ReportGenerationAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
        ),
        AgentTarget.HUMAN_REVIEW: HumanReviewAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
        ),
    }

    graph = StateGraph(WorkflowState)
    graph.add_node("route", _route_node(router))

    for target, agent in agents.items():
        graph.add_node(target.value, _agent_node(agent))
        graph.add_edge(target.value, "route")

    graph.add_edge(START, "route")
    graph.add_conditional_edges(
        "route",
        lambda state: state["last_decision"].target_agent.value,
        {
            AgentTarget.RESEARCH.value: AgentTarget.RESEARCH.value,
            AgentTarget.RISK_SCORING.value: AgentTarget.RISK_SCORING.value,
            AgentTarget.COMPLIANCE_REVIEW.value: AgentTarget.COMPLIANCE_REVIEW.value,
            AgentTarget.REPORT.value: AgentTarget.REPORT.value,
            AgentTarget.HUMAN_REVIEW.value: AgentTarget.HUMAN_REVIEW.value,
            AgentTarget.FINISH.value: END,
        },
    )
    return graph


def compile_graph() -> Any:
    return build_graph().compile()


def _route_node(router: PolicyRouter) -> Callable[[WorkflowState], dict[str, object]]:
    def route(state: WorkflowState) -> dict[str, object]:
        decision = router.route(state)
        history = [*state.get("routing_history", []), decision]
        return {
            "last_decision": decision,
            "routing_history": history,
        }

    return route


def _agent_node(agent: BaseAgent) -> Callable[[WorkflowState], Any]:
    async def run(state: WorkflowState) -> dict[str, object]:
        result = await agent.run(state)
        return result.state_updates

    return run
