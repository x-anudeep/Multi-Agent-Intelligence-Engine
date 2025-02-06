from __future__ import annotations

import tempfile
import unittest

from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings
from maie.evaluation.harness import WorkflowEvaluationHarness


class WorkflowEvaluationHarnessTests(unittest.IsolatedAsyncioTestCase):
    async def test_harness_scores_sample_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(
                checkpoint_dir=temp_dir,
                enable_telemetry=False,
                enable_governance=True,
            )
            service = WorkflowApplicationService(settings)
            harness = WorkflowEvaluationHarness(service)
            cases = harness.load_cases("examples/evals/phase4_eval_cases.json")

            summary = await harness.evaluate_cases(cases)

        self.assertEqual(summary.total_cases, 2)
        self.assertGreaterEqual(summary.passed_cases, 2)
        self.assertGreater(summary.average_observed_risk_score, 0)


if __name__ == "__main__":
    unittest.main()

