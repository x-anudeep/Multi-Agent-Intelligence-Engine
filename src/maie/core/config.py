from __future__ import annotations

import os
from dataclasses import asdict, dataclass


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    app_name: str = "multi-agent-intelligence-engine"
    app_version: str = "2.0.0"
    environment: str = "local"
    domain_context: str = "financial-services"
    redis_url: str = "redis://localhost:6379/0"
    postgres_url: str = "postgresql://postgres:postgres@localhost:5432/maie"
    checkpoint_dir: str = ".maie/checkpoints"
    use_mock_providers: bool = True
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
            use_mock_providers=_as_bool(os.getenv("USE_MOCK_PROVIDERS"), True),
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
