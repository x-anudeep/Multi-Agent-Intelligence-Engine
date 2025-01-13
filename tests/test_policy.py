from __future__ import annotations

import unittest

from maie.domain.models import AgentTarget, RiskAssessment, SignalSource, SupplierSignal
from maie.graph.state import build_initial_state
from maie.routing.policy import PolicyRouter


class PolicyRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = PolicyRouter()
        self.signal = SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.NEWS,
            headline="Factory outage",
            summary="A regional outage impacted production lines.",
            severity=4,
            region="US",
        )

    def test_routes_to_research_when_no_notes_exist(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.RESEARCH)

    def test_routes_to_risk_scoring_after_research(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.RISK_SCORING)

    def test_routes_to_human_review_when_policy_is_triggered(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        state["risk_assessment"] = RiskAssessment(
            supplier_name="Apex Components",
            overall_risk_score=90,
            disruption_probability=0.9,
            explanation="High risk.",
            evidence=["SEC filing"],
            recommended_actions=["Escalate"],
            requires_human_review=True,
        )
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.HUMAN_REVIEW)

    def test_routes_to_report_when_scoring_is_complete(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        state["risk_assessment"] = RiskAssessment(
            supplier_name="Apex Components",
            overall_risk_score=60,
            disruption_probability=0.6,
            explanation="Medium risk.",
            evidence=["News signal"],
            recommended_actions=["Watch closely"],
            requires_human_review=False,
        )
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.REPORT)


if __name__ == "__main__":
    unittest.main()

