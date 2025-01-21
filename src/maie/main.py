from __future__ import annotations

import asyncio
import json

from maie.core.config import Settings
from maie.domain.models import SignalSource, SupplierSignal
from maie.graph.state import serialize_state
from maie.runtime.engine import build_default_engine


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
    engine = build_default_engine(settings)
    artifacts = await engine.run("Apex Components", signals)
    return {
        "settings": settings.to_redacted_dict(),
        "checkpoints": {
            "count": len(artifacts.checkpoint_records),
            "location": artifacts.checkpoint_location,
        },
        "telemetry": artifacts.telemetry.summarize(),
        "state": serialize_state(artifacts.state),
    }


def main() -> None:
    payload = asyncio.run(_run())
    print(json.dumps(payload, indent=2))
