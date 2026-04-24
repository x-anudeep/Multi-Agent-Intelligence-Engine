from __future__ import annotations

import tempfile
import unittest

from maie.core.config import Settings
from maie.demo.service import LiveDemoService


class LiveDemoServiceTests(unittest.IsolatedAsyncioTestCase):
    def test_demo_service_can_draft_plain_english_scenarios(self) -> None:
        service = LiveDemoService(Settings(enable_telemetry=False))

        drafted = service.draft_scenario(
            "Supplier Apex Components disclosed debt covenant pressure in an SEC filing while "
            "North America port congestion delayed semiconductor shipments for 10 days."
        )

        self.assertEqual(drafted["request"]["supplier_name"], "Apex Components")
        self.assertGreaterEqual(len(drafted["request"]["signals"]), 2)
        self.assertIn("sec_filing", [signal["source"] for signal in drafted["request"]["signals"]])

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

        self.assertGreaterEqual(len(scenarios), 6)
        self.assertEqual(result["workflow"]["status"], "complete")
        self.assertTrue(result["dashboard"]["routing_targets"])
        self.assertIn("checkpoint_count", result["dashboard"])
        self.assertIn("snapshot_count", result["dashboard"])
        self.assertIn("average_event_duration_ms", result["dashboard"])
        self.assertIn("compliance_review", result["dashboard"])


if __name__ == "__main__":
    unittest.main()
