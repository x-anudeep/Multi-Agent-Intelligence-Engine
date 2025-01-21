from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from maie.domain.models import AgentTarget, ProviderName
from maie.graph.state import WorkflowState

if TYPE_CHECKING:
    from maie.providers.registry import ProviderRegistry
    from maie.tools.registry import ToolRegistry


@dataclass(slots=True)
class AgentExecutionResult:
    agent_name: AgentTarget
    state_updates: dict[str, object]
    audit_log: str


class BaseAgent(ABC):
    name: AgentTarget
    provider: ProviderName

    def __init__(
        self,
        *,
        provider_registry: "ProviderRegistry | None" = None,
        tool_registry: "ToolRegistry | None" = None,
    ) -> None:
        self.provider_registry = provider_registry
        self.tool_registry = tool_registry

    def _require_provider_registry(self) -> "ProviderRegistry":
        if self.provider_registry is None:
            raise RuntimeError(f"{self.name.value} requires a provider registry.")
        return self.provider_registry

    @abstractmethod
    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        raise NotImplementedError
