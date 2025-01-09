from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from maie.domain.models import AgentTarget, ProviderName
from maie.graph.state import WorkflowState


@dataclass(slots=True)
class AgentExecutionResult:
    agent_name: AgentTarget
    state_updates: dict[str, object]
    audit_log: str


class BaseAgent(ABC):
    name: AgentTarget
    provider: ProviderName

    @abstractmethod
    async def run(self, state: WorkflowState) -> AgentExecutionResult:
        raise NotImplementedError

