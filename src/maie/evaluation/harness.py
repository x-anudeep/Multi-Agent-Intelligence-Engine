from __future__ import annotations

import json
from pathlib import Path

from maie.application.workflow_service import WorkflowApplicationService
from maie.evaluation.contracts import (
    EvaluationCase,
    EvaluationCaseResult,
    EvaluationSummary,
)


class WorkflowEvaluationHarness:
    def __init__(
        self,
        service: WorkflowApplicationService,
    ) -> None:
        self.service = service
        self.risk_score_tolerance = service.settings.eval_risk_score_tolerance

    async def evaluate_cases(self, cases: list[EvaluationCase]) -> EvaluationSummary:
        results: list[EvaluationCaseResult] = []
        observed_scores: list[int] = []

        for case in cases:
            response = await self.service.execute_risk_workflow(case.request)
            reasons: list[str] = []
            status_match = response.status == case.expectation.expected_status
            if not status_match:
                reasons.append(
                    f"Expected status {case.expectation.expected_status}, got {response.status}."
                )

            human_review_match = True
            if case.expectation.expected_requires_human_review is not None:
                human_review_match = (
                    response.requires_human_review
                    == case.expectation.expected_requires_human_review
                )
                if not human_review_match:
                    reasons.append("Human review expectation did not match observed workflow.")

            risk_score_match = True
            if case.expectation.expected_min_risk_score is not None:
                risk_score_match = (
                    response.overall_risk_score is not None
                    and response.overall_risk_score
                    >= case.expectation.expected_min_risk_score - self.risk_score_tolerance
                )
                if not risk_score_match:
                    reasons.append("Observed risk score was lower than the expected minimum.")

            if (
                risk_score_match
                and case.expectation.expected_max_risk_score is not None
            ):
                risk_score_match = (
                    response.overall_risk_score is not None
                    and response.overall_risk_score
                    <= case.expectation.expected_max_risk_score + self.risk_score_tolerance
                )
                if not risk_score_match:
                    reasons.append("Observed risk score was higher than the expected maximum.")

            route_match = all(
                target in response.routing_targets
                for target in case.expectation.required_route_targets
            )
            if not route_match:
                reasons.append("Observed routing path missed one or more required targets.")

            passed = status_match and risk_score_match and human_review_match and route_match
            if response.overall_risk_score is not None:
                observed_scores.append(response.overall_risk_score)
            results.append(
                EvaluationCaseResult(
                    case_id=case.case_id,
                    passed=passed,
                    status_match=status_match,
                    risk_score_match=risk_score_match,
                    human_review_match=human_review_match,
                    route_match=route_match,
                    observed_risk_score=response.overall_risk_score,
                    observed_requires_human_review=response.requires_human_review,
                    reasons=reasons,
                )
            )

        total_cases = len(results)
        passed_cases = sum(1 for result in results if result.passed)
        average_score = (
            round(sum(observed_scores) / len(observed_scores), 2)
            if observed_scores
            else 0.0
        )
        pass_rate = round((passed_cases / total_cases) * 100, 2) if total_cases else 0.0
        return EvaluationSummary(
            total_cases=total_cases,
            passed_cases=passed_cases,
            pass_rate=pass_rate,
            average_observed_risk_score=average_score,
            results=results,
        )

    @staticmethod
    def load_cases(path: str | Path) -> list[EvaluationCase]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return [EvaluationCase.model_validate(item) for item in payload["cases"]]
