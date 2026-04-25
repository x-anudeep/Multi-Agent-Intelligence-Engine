from __future__ import annotations

import asyncio
import unittest

from maie.core.config import Settings
from maie.domain.models import ProviderName, SignalSource, SupplierSignal
from maie.providers.gemini import GeminiProvider
from maie.providers.ollama import OllamaProvider
from maie.providers.openrouter import OpenRouterProvider
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

    def test_gemini_key_registers_live_vertex_provider(self) -> None:
        registry = build_default_provider_registry(
            Settings(
                use_mock_providers=False,
                gemini_api_key="test-key",
                gemini_model="gemini-2.5-flash",
            )
        )

        self.assertIsInstance(registry.get(ProviderName.VERTEX_AI), GeminiProvider)

    def test_ollama_key_registers_live_ollama_provider(self) -> None:
        registry = build_default_provider_registry(
            Settings(
                use_mock_providers=False,
                ollama_api_key="test-key",
                ollama_model="gpt-oss:120b",
            )
        )

        self.assertIsInstance(registry.get(ProviderName.OLLAMA), OllamaProvider)

    def test_openrouter_key_registers_live_openrouter_provider(self) -> None:
        registry = build_default_provider_registry(
            Settings(
                use_mock_providers=False,
                openrouter_api_key="test-key",
                openrouter_model="openai/gpt-oss-120b:free",
            )
        )

        self.assertIsInstance(registry.get(ProviderName.OPENROUTER), OpenRouterProvider)


if __name__ == "__main__":
    unittest.main()
