from __future__ import annotations

import tempfile
import unittest

from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings
from maie.evaluation.benchmark import WorkflowBenchmarkRunner
from maie.evaluation.harness import WorkflowEvaluationHarness


class WorkflowBenchmarkRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_benchmark_reports_latency_and_snapshot_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(
                checkpoint_dir=temp_dir,
                enable_telemetry=False,
                checkpoint_backend="sqlite",
                state_backend="memory",
            )
            service = WorkflowApplicationService(settings)
            harness = WorkflowEvaluationHarness(service)
            cases = harness.load_cases("examples/evals/benchmark_cases.json")
            runner = WorkflowBenchmarkRunner(service)

            summary = await runner.run(cases)

        self.assertEqual(summary.total_cases, 3)
        self.assertGreater(summary.pass_rate, 0)
        self.assertGreater(summary.average_latency_ms, 0)
        self.assertGreater(summary.total_snapshots, 0)
        self.assertGreaterEqual(summary.max_routing_branch_count, 3)


if __name__ == "__main__":
    unittest.main()
