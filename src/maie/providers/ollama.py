from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from maie.domain.models import ProviderName
from maie.providers.base import BaseModelProvider, ModelOutput


class OllamaProvider(BaseModelProvider):
    def __init__(self, *, api_key: str, model_id: str, host: str = "https://ollama.com") -> None:
        if not api_key:
            raise ValueError("Ollama API key is required for OllamaProvider.")
        super().__init__(ProviderName.OLLAMA, model_id)
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
                "summary": "Ollama generated text output.",
            },
        )

    async def generate_structured(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        if task_name == "compliance_review":
            prompt = _build_compliance_prompt(context)
        else:
            prompt = "\n".join([_build_prompt(task_name, context), "Return valid JSON only."])
        content = await asyncio.to_thread(self._chat, prompt)
        payload = _loads_json(content)
        if task_name == "compliance_review":
            payload = _normalize_compliance_payload(payload)
        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content=content,
            structured_content=payload,
            metadata={
                "model_id": self.model_id,
                "summary": f"Ollama generated structured {task_name} output.",
            },
        )

    def _chat(self, prompt: str) -> str:
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        request = Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=60) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama API request failed with HTTP {error.code}: {details}") from error
        except URLError as error:
            raise RuntimeError(f"Ollama API request failed: {error.reason}") from error

        try:
            return str(response_payload["message"]["content"]).strip()
        except KeyError as error:
            raise RuntimeError(f"Ollama API returned an unexpected response: {response_payload}") from error


def _build_prompt(task_name: str, context: dict[str, Any]) -> str:
    if task_name == "report_generation":
        return "\n".join(
            [
                "Write a concise executive supplier-risk brief for a financial-services audience.",
                "Use Markdown headings.",
                "Include risk score, disruption probability, compliance posture, recommended actions, and recovery plan.",
                "",
                json.dumps(context, indent=2, default=str),
            ]
        )
    return "\n".join(
        [
            f"Task: {task_name}",
            "Use the supplied workflow context and produce a concise enterprise risk workflow response.",
            json.dumps(context, indent=2, default=str),
        ]
    )


def _build_compliance_prompt(context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are a financial-services supplier-risk compliance reviewer.",
            "Return valid JSON only. Do not include markdown.",
            "Your JSON must contain exactly these fields:",
            "- status: string",
            "- summary: string",
            "- obligations: array of strings",
            "- mitigation_plan: array of strings",
            "- requires_human_signoff: boolean",
            "- blocking_findings: array of strings",
            "",
            "Rules:",
            "- If there is an SEC filing, debt covenant issue, liquidity issue, cross-border exposure, or risk score >= 80, require human signoff.",
            "- Use status 'conditional_approval' when human signoff is required.",
            "- Put serious issues in blocking_findings.",
            "- Include concrete mitigation actions.",
            "",
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
        raise RuntimeError(f"Ollama returned invalid JSON: {value}") from error


def _normalize_compliance_payload(payload: dict[str, Any]) -> dict[str, object]:
    status = str(payload.get("status") or "conditional_approval")
    obligations = payload.get("obligations") or [
        "Document supplier risk rationale and escalation decision.",
        "Notify procurement and risk operations for high-impact supplier exposure.",
    ]
    mitigation_plan = payload.get("mitigation_plan") or [
        "Validate alternate supplier capacity.",
        "Open a daily monitoring cadence until supplier risk falls below threshold.",
    ]
    blocking_findings = payload.get("blocking_findings") or []
    requires_human_signoff = bool(
        payload.get("requires_human_signoff")
        or status == "conditional_approval"
        or blocking_findings
    )
    return {
        "status": status,
        "summary": str(
            payload.get(
                "summary",
                "Ollama compliance review validated supplier-risk controls and escalation needs.",
            )
        ),
        "obligations": [str(item) for item in obligations],
        "mitigation_plan": [str(item) for item in mitigation_plan],
        "requires_human_signoff": requires_human_signoff,
        "blocking_findings": [str(item) for item in blocking_findings],
    }
