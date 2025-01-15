from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from maie.domain.models import ProviderName


@dataclass(slots=True)
class ModelOutput:
    provider: ProviderName
    task_name: str
    content: str
    structured_content: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider.value,
            "task_name": self.task_name,
            "content": self.content,
            "structured_content": self.structured_content,
            "metadata": self.metadata,
        }


class BaseModelProvider(ABC):
    def __init__(self, name: ProviderName, model_id: str) -> None:
        self.name = name
        self.model_id = model_id

    @abstractmethod
    async def generate_text(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        raise NotImplementedError

    @abstractmethod
    async def generate_structured(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        raise NotImplementedError

