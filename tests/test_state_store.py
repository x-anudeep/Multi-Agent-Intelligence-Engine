from __future__ import annotations

import unittest

from maie.domain.models import SignalSource, SupplierSignal
from maie.graph.state import build_initial_state
from maie.runtime.state_store import InMemoryRuntimeStateStore


class InMemoryRuntimeStateStoreTests(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        signal = SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.NEWS,
            headline="Factory outage",
            summary="Production slowed after an outage.",
            severity=4,
            region="US",
        )
        state = build_initial_state("Apex Components", [signal])
        store = InMemoryRuntimeStateStore()

        store.save_snapshot(state["workflow_id"], "initialized", state)
        records = store.load_snapshots(state["workflow_id"])

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].label, "initialized")


if __name__ == "__main__":
    unittest.main()
