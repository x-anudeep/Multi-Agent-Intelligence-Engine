from __future__ import annotations

import asyncio
import json
import sys

from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings
from maie.evaluation.harness import WorkflowEvaluationHarness


def main() -> None:
    dataset_path = (
        sys.argv[1] if len(sys.argv) > 1 else "examples/evals/phase4_eval_cases.json"
    )
    summary = asyncio.run(_run(dataset_path))
    print(json.dumps(summary.model_dump(), indent=2))


async def _run(dataset_path: str) -> object:
    settings = Settings.from_env()
    service = WorkflowApplicationService(settings)
    harness = WorkflowEvaluationHarness(service)
    cases = harness.load_cases(dataset_path)
    return await harness.evaluate_cases(cases)


if __name__ == "__main__":
    main()
