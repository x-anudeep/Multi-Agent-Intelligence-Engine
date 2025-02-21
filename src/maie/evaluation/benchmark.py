from __future__ import annotations

from math import ceil
from statistics import mean
from time import perf_counter

from maie.application.workflow_service import WorkflowApplicationService
from maie.evaluation.contracts import BenchmarkCaseResult, BenchmarkSummary, EvaluationCase
from maie.evaluation.harness import WorkflowEvaluationHarness


class WorkflowBenchmarkRunner:
    def __init__(self, service: WorkflowApplicationService) -> None:
        self.service = service
        self.harness = WorkflowEvaluationHarness(service)

    async def run(self, cases: list[EvaluationCase]) -> BenchmarkSummary:
        results: list[BenchmarkCaseResult] = []

        for case in cases:
            started_at = perf_counter()
            response = await self.service.execute_risk_workflow(case.request)
            latency_ms = round((perf_counter() - started_at) * 1000, 2)
            evaluation = await self.harness.evaluate_cases([case])
            passed = evaluation.results[0].passed
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    passed=passed,
                    latency_ms=latency_ms,
                    checkpoint_count=response.checkpoint_count,
                    snapshot_count=response.snapshot_count,
                    routing_branch_count=response.routing_branch_count,
                    telemetry_event_count=response.telemetry_event_count,
                )
            )

        latencies = sorted(result.latency_ms for result in results)
        p95_index = max(ceil(len(latencies) * 0.95) - 1, 0) if latencies else 0
        return BenchmarkSummary(
            total_cases=len(results),
            pass_rate=round(
                (sum(1 for result in results if result.passed) / len(results)) * 100,
                2,
            )
            if results
            else 0.0,
            average_latency_ms=round(mean(latencies), 2) if latencies else 0.0,
            p95_latency_ms=latencies[p95_index] if latencies else 0.0,
            total_checkpoints=sum(result.checkpoint_count for result in results),
            total_snapshots=sum(result.snapshot_count for result in results),
            total_telemetry_events=sum(result.telemetry_event_count for result in results),
            max_routing_branch_count=max(
                (result.routing_branch_count for result in results),
                default=0,
            ),
            results=results,
        )
