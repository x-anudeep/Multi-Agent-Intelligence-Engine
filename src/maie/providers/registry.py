from __future__ import annotations

from maie.core.config import Settings
from maie.domain.models import ProviderName
from maie.providers.base import BaseModelProvider
from maie.providers.gemini import GeminiProvider
from maie.providers.mock import MockProvider
from maie.providers.ollama import OllamaProvider
from maie.providers.openrouter import OpenRouterProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[ProviderName, BaseModelProvider] = {}

    def register(self, provider: BaseModelProvider) -> None:
        if provider.name in self._providers:
            raise ValueError(f"Provider '{provider.name.value}' is already registered.")
        self._providers[provider.name] = provider

    def get(self, provider_name: ProviderName) -> BaseModelProvider:
        try:
            return self._providers[provider_name]
        except KeyError as error:
            raise KeyError(f"Provider '{provider_name.value}' is not registered.") from error

    def list_names(self) -> list[str]:
        return sorted(provider.value for provider in self._providers)


def build_default_provider_registry(settings: Settings) -> ProviderRegistry:
    registry = ProviderRegistry()
    if not settings.use_mock_providers:
        if settings.gemini_api_key:
            registry.register(
                GeminiProvider(
                    api_key=settings.gemini_api_key,
                    model_id=settings.gemini_model or "gemini-2.5-flash",
                )
            )
        if settings.ollama_api_key:
            registry.register(
                OllamaProvider(
                    api_key=settings.ollama_api_key,
                    model_id=settings.ollama_model,
                    host=settings.ollama_host,
                )
            )
        if settings.openrouter_api_key:
            registry.register(
                OpenRouterProvider(
                    api_key=settings.openrouter_api_key,
                    model_id=settings.openrouter_model,
                    host=settings.openrouter_host,
                )
            )
        return registry

    registry.register(
        MockProvider(
            name=ProviderName.OPENAI,
            model_id="offline-openai-test-provider",
        )
    )
    registry.register(
        MockProvider(
            name=ProviderName.ANTHROPIC,
            model_id="offline-anthropic-test-provider",
        )
    )
    registry.register(
        MockProvider(
            name=ProviderName.VERTEX_AI,
            model_id="offline-gemini-test-provider",
        )
    )
    return registry
