from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from maie.domain.models import ProviderName
from maie.providers.base import BaseModelProvider, ModelOutput


class OpenRouterProvider(BaseModelProvider):
    def __init__(
        self,
        *,
        api_key: str,
        model_id: str,
        host: str = "https://openrouter.ai/api/v1",
    ) -> None:
        if not api_key:
            raise ValueError("OpenRouter API key is required for OpenRouterProvider.")
        super().__init__(ProviderName.OPENROUTER, model_id)
        self.api_key = api_key
        self.host = host.rstrip("/")

    async def generate_text(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        prompt = _build_prompt(task_name, context)
        content = await asyncio.to_thread(self._chat, prompt)
        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content=content,
            metadata={
                "model_id": self.model_id,
                "summary": "OpenRouter generated text output.",
            },
        )

    async def generate_structured(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        prompt = "\n".join([_build_prompt(task_name, context), "Return valid JSON only."])
        content = await asyncio.to_thread(self._chat, prompt)
        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content=content,
            structured_content=_loads_json(content),
            metadata={
                "model_id": self.model_id,
                "summary": "OpenRouter generated structured output.",
            },
        )

    def _chat(self, prompt: str) -> str:
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
        }
        request = Request(
            f"{self.host}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8091",
                "X-Title": "Multi-Agent Intelligence Engine",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=90) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenRouter API request failed with HTTP {error.code}: {details}"
            ) from error
        except URLError as error:
            raise RuntimeError(f"OpenRouter API request failed: {error.reason}") from error

        try:
            return str(response_payload["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError) as error:
            raise RuntimeError(
                f"OpenRouter API returned an unexpected response: {response_payload}"
            ) from error


def _build_prompt(task_name: str, context: dict[str, Any]) -> str:
    if task_name == "report_generation":
        return "\n".join(
            [
                "Write the final executive supplier-risk report for a financial-services team.",
                "Use polished, concise Markdown that will render inside a web dashboard.",
                "Use short paragraphs and bullet lists. Do not use tables.",
                "Include these sections: Supplier Risk Brief, Executive Summary, Compliance Outcome, Recommended Actions, Recovery Plan.",
                "Start with a one-line risk posture statement.",
                "Do not mention internal provider names.",
                "",
                json.dumps(context, indent=2, default=str),
            ]
        )
    return "\n".join(
        [
            f"Task: {task_name}",
            "Use the supplied workflow context and produce a concise response.",
            json.dumps(context, indent=2, default=str),
        ]
    )


def _loads_json(value: str) -> dict[str, Any]:
    cleaned = value.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()
    if not cleaned.startswith("{") and "{" in cleaned and "}" in cleaned:
        cleaned = cleaned[cleaned.find("{") : cleaned.rfind("}") + 1]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"OpenRouter returned invalid JSON: {value}") from error
