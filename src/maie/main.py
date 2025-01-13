from __future__ import annotations

import asyncio
import json

from maie.core.config import Settings
from maie.domain.models import SignalSource, SupplierSignal
from maie.graph.state import serialize_state
from maie.runtime.simulator import run_local_simulation


async def _run() -> dict[str, object]:
    settings = Settings.from_env()
    signals = [
        SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.NEWS,
            headline="Port congestion delays high-value semiconductor shipments",
            summary="Major logistics bottlenecks are extending shipment timelines by 10 days.",
            severity=4,
            region="North America",
        ),
        SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.SEC_FILING,
            headline="Supplier disclosed material uncertainty tied to debt covenants",
            summary="Latest filing highlights liquidity pressure and refinancing risk.",
            severity=5,
            region="United States",
        ),
    ]
    final_state = await run_local_simulation("Apex Components", signals)
    return {
        "settings": settings.to_redacted_dict(),
        "state": serialize_state(final_state),
    }


def main() -> None:
    payload = asyncio.run(_run())
    print(json.dumps(payload, indent=2))

