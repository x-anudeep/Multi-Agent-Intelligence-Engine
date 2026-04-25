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
        state["collected_evidence"] = ["Research evidence"]
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.RISK_SCORING)

    def test_routes_to_human_review_when_policy_is_triggered(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        state["collected_evidence"] = ["Research evidence"]
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

    def test_routes_to_compliance_review_for_regulatory_signals(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        state["collected_evidence"] = ["Factory outage evidence"]
        state["risk_assessment"] = RiskAssessment(
            supplier_name="Apex Components",
            overall_risk_score=72,
            disruption_probability=0.72,
            explanation="Elevated risk.",
            evidence=["News signal"],
            recommended_actions=["Review controls"],
            requires_human_review=False,
        )
        state["jurisdiction"] = "DE"
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.COMPLIANCE_REVIEW)

    def test_routes_to_compliance_for_every_completed_score(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        state["collected_evidence"] = ["News signal"]
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
        self.assertEqual(decision.target_agent, AgentTarget.COMPLIANCE_REVIEW)

    def test_routes_back_to_human_review_when_compliance_blocks_reporting(self) -> None:
        state = build_initial_state("Apex Components", [self.signal])
        state["research_notes"] = ["Research complete"]
        state["collected_evidence"] = ["News signal"]
        state["risk_assessment"] = RiskAssessment(
            supplier_name="Apex Components",
            overall_risk_score=88,
            disruption_probability=0.88,
            explanation="High risk.",
            evidence=["News signal"],
            recommended_actions=["Escalate"],
            requires_human_review=False,
        )
        state["compliance_blocked"] = True
        decision = self.router.route(state)
        self.assertEqual(decision.target_agent, AgentTarget.HUMAN_REVIEW)


if __name__ == "__main__":
    unittest.main()
