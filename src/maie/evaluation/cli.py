from __future__ import annotations

import asyncio
import json
import sys

from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings
from maie.evaluation.benchmark import WorkflowBenchmarkRunner
from maie.evaluation.harness import WorkflowEvaluationHarness


def main() -> None:
    args = sys.argv[1:]
    benchmark_mode = "--benchmark" in args
    dataset_args = [arg for arg in args if arg != "--benchmark"]
    dataset_path = dataset_args[0] if dataset_args else "examples/evals/workflow_eval_cases.json"
    summary = asyncio.run(_run(dataset_path, benchmark_mode=benchmark_mode))
    print(json.dumps(summary.model_dump(), indent=2))


async def _run(dataset_path: str, *, benchmark_mode: bool = False) -> object:
    settings = Settings.from_env()
    service = WorkflowApplicationService(settings)
    harness = WorkflowEvaluationHarness(service)
    cases = harness.load_cases(dataset_path)
    if benchmark_mode:
        runner = WorkflowBenchmarkRunner(service)
        return await runner.run(cases)
    return await harness.evaluate_cases(cases)


if __name__ == "__main__":
    main()
