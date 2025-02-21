from __future__ import annotations

import os
from dataclasses import asdict, dataclass


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    return int(value)


@dataclass(slots=True)
class Settings:
    app_name: str = "multi-agent-intelligence-engine"
    app_version: str = "2.0.0"
    environment: str = "local"
    domain_context: str = "financial-services"
    redis_url: str = "redis://localhost:6379/0"
    postgres_url: str = "postgresql://postgres:postgres@localhost:5432/maie"
    checkpoint_dir: str = ".maie/checkpoints"
    checkpoint_backend: str = "sqlite"
    state_backend: str = "memory"
    use_mock_providers: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_workers: int = 1
    demo_host: str = "127.0.0.1"
    demo_port: int = 8090
    knowledge_dir: str = "knowledge/financial-services"
    enable_governance: bool = True
    eval_risk_score_tolerance: int = 15
    openai_api_key: str = ""
    openai_model: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = ""
    vertex_project_id: str = ""
    vertex_location: str = "us-central1"
    vertex_model: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = "maie-v2"
    enable_telemetry: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_version=os.getenv("APP_VERSION", "2.0.0"),
            environment=os.getenv("APP_ENV", "local"),
            domain_context=os.getenv("DOMAIN_CONTEXT", "financial-services"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            postgres_url=os.getenv(
                "POSTGRES_URL",
                "postgresql://postgres:postgres@localhost:5432/maie",
            ),
            checkpoint_dir=os.getenv("CHECKPOINT_DIR", ".maie/checkpoints"),
            checkpoint_backend=os.getenv("CHECKPOINT_BACKEND", "sqlite"),
            state_backend=os.getenv("STATE_BACKEND", "memory"),
            use_mock_providers=_as_bool(os.getenv("USE_MOCK_PROVIDERS"), True),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=_as_int(os.getenv("API_PORT"), 8080),
            api_workers=_as_int(os.getenv("API_WORKERS"), 1),
            demo_host=os.getenv("DEMO_HOST", "127.0.0.1"),
            demo_port=_as_int(os.getenv("DEMO_PORT"), 8090),
            knowledge_dir=os.getenv("KNOWLEDGE_DIR", "knowledge/financial-services"),
            enable_governance=_as_bool(os.getenv("ENABLE_GOVERNANCE"), True),
            eval_risk_score_tolerance=_as_int(os.getenv("EVAL_RISK_SCORE_TOLERANCE"), 15),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", ""),
            vertex_project_id=os.getenv("VERTEX_PROJECT_ID", ""),
            vertex_location=os.getenv("VERTEX_LOCATION", "us-central1"),
            vertex_model=os.getenv("VERTEX_MODEL", ""),
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY", ""),
            langsmith_project=os.getenv("LANGSMITH_PROJECT", "maie-v2"),
            enable_telemetry=_as_bool(os.getenv("ENABLE_TELEMETRY"), True),
        )

    def to_redacted_dict(self) -> dict[str, object]:
        redacted = asdict(self)
        for key in [
            "openai_api_key",
            "anthropic_api_key",
            "langsmith_api_key",
        ]:
            if redacted[key]:
                redacted[key] = "***redacted***"
        return redacted
