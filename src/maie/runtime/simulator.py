from __future__ import annotations

from maie.agents.base import BaseAgent
from maie.agents.specialists import (
    HumanReviewAgent,
    ReportGenerationAgent,
    ResearchAgent,
    RiskScoringAgent,
)
from maie.domain.models import AgentTarget, RoutingDecision, SupplierSignal, WorkflowStatus
from maie.graph.state import WorkflowState, build_initial_state
from maie.routing.policy import PolicyRouter


async def run_local_simulation(
    supplier_name: str,
    signals: list[SupplierSignal],
    *,
    max_steps: int = 8,
) -> WorkflowState:
    state = build_initial_state(supplier_name=supplier_name, signals=signals)
    router = PolicyRouter()
    agents: dict[AgentTarget, BaseAgent] = {
        AgentTarget.RESEARCH: ResearchAgent(),
        AgentTarget.RISK_SCORING: RiskScoringAgent(),
        AgentTarget.REPORT: ReportGenerationAgent(),
        AgentTarget.HUMAN_REVIEW: HumanReviewAgent(),
    }

    for _ in range(max_steps):
        decision = router.route(state)
        _record_decision(state, decision)
        if decision.target_agent is AgentTarget.FINISH:
            state["status"] = WorkflowStatus.COMPLETE.value
            return state

        result = await agents[decision.target_agent].run(state)
        state.update(result.state_updates)

    raise RuntimeError("Simulation exceeded the maximum number of steps.")


def _record_decision(state: WorkflowState, decision: RoutingDecision) -> None:
    history = [*state.get("routing_history", []), decision]
    state["last_decision"] = decision
    state["routing_history"] = history

