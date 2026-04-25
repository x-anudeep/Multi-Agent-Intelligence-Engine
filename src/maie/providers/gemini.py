from __future__ import annotations

import asyncio
import json
from typing import Any

from maie.domain.models import ProviderName
from maie.providers.base import BaseModelProvider, ModelOutput


class GeminiProvider(BaseModelProvider):
    def __init__(self, *, api_key: str, model_id: str) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required for GeminiProvider.")
        super().__init__(ProviderName.VERTEX_AI, model_id)
        self.api_key = api_key

    async def generate_text(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        prompt = _build_text_prompt(task_name, context)
        response_text = await asyncio.to_thread(self._generate, prompt, None)
        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content=response_text,
            metadata={
                "model_id": self.model_id,
                "summary": "Gemini generated text output.",
            },
        )

    async def generate_structured(self, task_name: str, context: dict[str, Any]) -> ModelOutput:
        if task_name != "risk_assessment":
            prompt = _build_text_prompt(task_name, context)
            response_text = await asyncio.to_thread(self._generate, prompt, _GENERIC_JSON_SCHEMA)
            return ModelOutput(
                provider=self.name,
                task_name=task_name,
                content=response_text,
                structured_content=_loads_json(response_text),
                metadata={
                    "model_id": self.model_id,
                    "summary": "Gemini generated structured output.",
                },
            )

        prompt = _build_risk_assessment_prompt(context)
        response_text = await asyncio.to_thread(self._generate, prompt, _RISK_ASSESSMENT_SCHEMA)
        payload = _loads_json(response_text)
        return ModelOutput(
            provider=self.name,
            task_name=task_name,
            content="Structured assessment complete.",
            structured_content=_normalize_risk_payload(payload),
            metadata={
                "model_id": self.model_id,
                "summary": "Gemini returned a structured risk assessment.",
            },
        )

    def _generate(self, prompt: str, schema: dict[str, Any] | None) -> str:
        try:
            from google import genai
        except ImportError as error:  # pragma: no cover
            raise RuntimeError(
                "google-genai is not installed. Run `python -m pip install -e .` first."
            ) from error

        client = genai.Client(api_key=self.api_key)
        config: dict[str, Any] = {}
        if schema is not None:
            config = {
                "response_mime_type": "application/json",
                "response_schema": schema,
            }

        response = client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=config or None,
        )
        return str(response.text or "").strip()


def _build_risk_assessment_prompt(context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are a supply-chain risk scoring agent for financial-services workflows.",
            "Return only JSON matching the provided schema.",
            "Score supplier disruption risk from 0 to 100.",
            "Set requires_human_review to true for SEC filings, material liquidity risk, severe outages, or scores >= 80.",
            "",
            f"Supplier: {context.get('supplier_name', 'Unknown supplier')}",
            f"Signals: {json.dumps(context.get('signals', []), indent=2)}",
            f"Evidence: {json.dumps(context.get('evidence', []), indent=2)}",
        ]
    )


def _build_text_prompt(task_name: str, context: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Task: {task_name}",
            "Use the supplied workflow context and produce a concise enterprise risk workflow response.",
            json.dumps(context, indent=2, default=str),
        ]
    )


def _loads_json(value: str) -> dict[str, Any]:
    try:
        return json.loads(value)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Gemini returned invalid JSON: {value}") from error


def _normalize_risk_payload(payload: dict[str, Any]) -> dict[str, object]:
    score = max(0, min(100, int(payload.get("overall_risk_score", 0))))
    probability = max(0.0, min(1.0, float(payload.get("disruption_probability", score / 100))))
    actions = payload.get("recommended_actions") or [
        "Review supplier exposure with procurement leadership.",
        "Validate alternate supplier options for affected regions.",
    ]
    return {
        "overall_risk_score": score,
        "disruption_probability": probability,
        "explanation": str(payload.get("explanation", "Gemini assessed supplier disruption risk.")),
        "recommended_actions": [str(action) for action in actions],
        "requires_human_review": bool(payload.get("requires_human_review", score >= 80)),
    }


_RISK_ASSESSMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_risk_score": {"type": "integer"},
        "disruption_probability": {"type": "number"},
        "explanation": {"type": "string"},
        "recommended_actions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "requires_human_review": {"type": "boolean"},
    },
    "required": [
        "overall_risk_score",
        "disruption_probability",
        "explanation",
        "recommended_actions",
        "requires_human_review",
    ],
}

_GENERIC_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
    },
    "required": ["summary"],
}
