from __future__ import annotations

from maie.core.config import Settings


def main() -> None:
    try:
        import uvicorn
    except ImportError as error:  # pragma: no cover
        raise RuntimeError(
            "Uvicorn is not installed. Install project dependencies to run the API server."
        ) from error

    settings = Settings.from_env()
    uvicorn.run(
        "maie.api.app:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
    )

