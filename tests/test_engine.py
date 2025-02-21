from __future__ import annotations

import tempfile
import unittest

from maie.core.config import Settings
from maie.domain.models import SignalSource, SupplierSignal
from maie.runtime.engine import build_default_engine


class WorkflowEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_engine_records_checkpoints_and_telemetry(self) -> None:
        signals = [
            SupplierSignal(
                supplier_name="Apex Components",
                source=SignalSource.NEWS,
                headline="Port congestion",
                summary="Logistics issues are affecting shipments.",
                severity=4,
                region="North America",
            ),
            SupplierSignal(
                supplier_name="Apex Components",
                source=SignalSource.SEC_FILING,
                headline="Liquidity warning",
                summary="Debt covenant risk disclosed in latest filing.",
                severity=5,
                region="US",
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(checkpoint_dir=temp_dir, enable_telemetry=False)
            engine = build_default_engine(settings)
            artifacts = await engine.run("Apex Components", signals)

        self.assertEqual(artifacts.state["status"], "complete")
        self.assertGreaterEqual(len(artifacts.checkpoint_records), 5)
        self.assertGreaterEqual(len(artifacts.snapshot_records), len(artifacts.checkpoint_records))
        self.assertGreaterEqual(artifacts.telemetry.summarize()["event_count"], 5)
        self.assertTrue(artifacts.state["tool_history"])
        self.assertTrue(artifacts.state["model_history"])
        self.assertTrue(artifacts.state["checkpoint_labels"])
        self.assertTrue(artifacts.state["snapshot_labels"])
        self.assertGreaterEqual(artifacts.state["snapshot_count"], len(artifacts.snapshot_records))
        self.assertIn("compliance_review_agent", [item.target_agent.value for item in artifacts.state["routing_history"]])


if __name__ == "__main__":
    unittest.main()
