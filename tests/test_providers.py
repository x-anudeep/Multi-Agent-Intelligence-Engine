from __future__ import annotations

import asyncio
import unittest

from maie.core.config import Settings
from maie.domain.models import ProviderName, SignalSource, SupplierSignal
from maie.providers.registry import build_default_provider_registry


class ProviderRegistryTests(unittest.TestCase):
    def test_default_registry_exposes_expected_providers(self) -> None:
        registry = build_default_provider_registry(Settings())
        self.assertEqual(
            registry.list_names(),
            ["anthropic", "openai", "vertex_ai"],
        )

    def test_vertex_provider_returns_structured_risk_payload(self) -> None:
        registry = build_default_provider_registry(Settings())
        provider = registry.get(ProviderName.VERTEX_AI)
        signal = SupplierSignal(
            supplier_name="Apex Components",
            source=SignalSource.SEC_FILING,
            headline="Liquidity warning",
            summary="Debt covenant risk disclosed in latest filing.",
            severity=5,
            region="US",
        )

        output = asyncio.run(
            provider.generate_structured(
                "risk_assessment",
                {
                    "supplier_name": "Apex Components",
                    "signals": [signal.to_dict()],
                    "evidence": [signal.summary],
                },
            )
        )

        self.assertGreaterEqual(int(output.structured_content["overall_risk_score"]), 80)
        self.assertTrue(bool(output.structured_content["requires_human_review"]))


if __name__ == "__main__":
    unittest.main()
