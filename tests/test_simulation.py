from __future__ import annotations

import unittest

from maie.domain.models import SignalSource, SupplierSignal
from maie.runtime.simulator import run_local_simulation


class SimulationTests(unittest.IsolatedAsyncioTestCase):
    async def test_local_simulation_reaches_completion(self) -> None:
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

        final_state = await run_local_simulation("Apex Components", signals)

        self.assertEqual(final_state["status"], "complete")
        self.assertIsNotNone(final_state["risk_assessment"])
        self.assertTrue(final_state["draft_report"])
        self.assertGreaterEqual(len(final_state["routing_history"]), 4)


if __name__ == "__main__":
    unittest.main()
