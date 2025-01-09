from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolHandler = Callable[..., Any]


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    handler: ToolHandler
    required_args: tuple[str, ...] = ()


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as error:
            raise KeyError(f"Tool '{name}' is not registered.") from error

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def invoke(self, name: str, **kwargs: Any) -> Any:
        tool = self.get(name)
        missing_args = [arg for arg in tool.required_args if arg not in kwargs]
        if missing_args:
            missing_args_text = ", ".join(missing_args)
            raise ValueError(f"Missing required tool arguments: {missing_args_text}")
        return tool.handler(**kwargs)

