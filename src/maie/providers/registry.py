from __future__ import annotations

from maie.core.config import Settings
from maie.domain.models import ProviderName
from maie.providers.base import BaseModelProvider
from maie.providers.mock import MockProvider


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
    openai_model = settings.openai_model or (
        "mock-openai-gpt" if settings.use_mock_providers else "configured-openai-model"
    )
    anthropic_model = settings.anthropic_model or (
        "mock-anthropic-claude" if settings.use_mock_providers else "configured-anthropic-model"
    )
    vertex_model = settings.vertex_model or (
        "mock-vertex-gemini" if settings.use_mock_providers else "configured-vertex-model"
    )
    registry.register(
        MockProvider(
            name=ProviderName.OPENAI,
            model_id=openai_model,
        )
    )
    registry.register(
        MockProvider(
            name=ProviderName.ANTHROPIC,
            model_id=anthropic_model,
        )
    )
    registry.register(
        MockProvider(
            name=ProviderName.VERTEX_AI,
            model_id=vertex_model,
        )
    )
    return registry
