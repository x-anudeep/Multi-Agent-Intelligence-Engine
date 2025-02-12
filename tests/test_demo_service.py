from __future__ import annotations

import tempfile
import unittest

from maie.core.config import Settings
from maie.demo.service import LiveDemoService


class LiveDemoServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_demo_service_lists_scenarios_and_runs_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(
                checkpoint_dir=temp_dir,
                enable_telemetry=False,
                enable_governance=True,
            )
            service = LiveDemoService(settings)
            scenarios = service.list_scenarios()

            result = await service.run_workflow(scenarios[0]["request"])

        self.assertGreaterEqual(len(scenarios), 3)
        self.assertEqual(result["workflow"]["status"], "complete")
        self.assertTrue(result["dashboard"]["routing_targets"])
        self.assertIn("checkpoint_count", result["dashboard"])


if __name__ == "__main__":
    unittest.main()

