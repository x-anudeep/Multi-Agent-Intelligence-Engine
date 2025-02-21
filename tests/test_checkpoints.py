from __future__ import annotations

import tempfile
import unittest

from maie.checkpoints.store import JsonFileCheckpointStore, SQLiteCheckpointStore
from maie.domain.models import SignalSource, SupplierSignal
from maie.graph.state import build_initial_state


class JsonFileCheckpointStoreTests(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        signal = SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.NEWS,
            headline="Factory outage",
            summary="Production slowed after an outage.",
            severity=4,
            region="US",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonFileCheckpointStore(temp_dir)
            state = build_initial_state("Apex Components", [signal])
            store.save(state["workflow_id"], "initialized", state)

            records = store.load(state["workflow_id"])

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].label, "initialized")


class SQLiteCheckpointStoreTests(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        signal = SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.NEWS,
            headline="Factory outage",
            summary="Production slowed after an outage.",
            severity=4,
            region="US",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            store = SQLiteCheckpointStore(f"{temp_dir}/checkpoints.sqlite3")
            state = build_initial_state("Apex Components", [signal])
            store.save(state["workflow_id"], "initialized", state)

            records = store.load(state["workflow_id"])

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].label, "initialized")


if __name__ == "__main__":
    unittest.main()
