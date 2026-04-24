from __future__ import annotations

import asyncio
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
from typing import Any
from urllib.parse import urlparse

from pydantic import ValidationError

from maie.core.config import Settings
from maie.demo.service import LiveDemoService


ASSET_CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def create_demo_server(
    *,
    host: str,
    port: int,
    settings: Settings | None = None,
) -> ThreadingHTTPServer:
    resolved_settings = settings or Settings.from_env()
    service = LiveDemoService(resolved_settings)
    handler = partial(DemoRequestHandler, demo_service=service)
    return ThreadingHTTPServer((host, port), handler)


class DemoRequestHandler(BaseHTTPRequestHandler):
    def __init__(
        self,
        *args: Any,
        demo_service: LiveDemoService,
        **kwargs: Any,
    ) -> None:
        self.demo_service = demo_service
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._serve_asset("index.html")
            return
        if path == "/assets/styles.css":
            self._serve_asset("styles.css")
            return
        if path == "/assets/app.js":
            self._serve_asset("app.js")
            return
        if path == "/api/demo/health":
            self._send_json(HTTPStatus.OK, self.demo_service.health_payload())
            return
        if path == "/api/demo/scenarios":
            self._send_json(HTTPStatus.OK, {"scenarios": self.demo_service.list_scenarios()})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be valid JSON."})
            return

        if path == "/api/demo/run":
            try:
                result = asyncio.run(self.demo_service.run_workflow(payload))
            except ValidationError as error:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "error": "Workflow request validation failed.",
                        "details": error.errors(),
                    },
                )
                return
            except Exception as error:  # pragma: no cover
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": "Live demo execution failed.", "details": str(error)},
                )
                return

            self._send_json(HTTPStatus.OK, result)
            return

        if path == "/api/demo/draft-scenario":
            try:
                drafted = self.demo_service.draft_scenario(str(payload.get("prompt", "")))
            except ValueError as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return
            except ValidationError as error:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "error": "Scenario drafting failed validation.",
                        "details": error.errors(),
                    },
                )
                return

            self._send_json(HTTPStatus.OK, drafted)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def _serve_asset(self, asset_name: str) -> None:
        resource = files("maie.demo").joinpath("web", asset_name)
        if not resource.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Asset not found."})
            return

        suffix = resource.name[resource.name.rfind(".") :]
        payload = resource.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-Type",
            ASSET_CONTENT_TYPES.get(suffix, "application/octet-stream"),
        )
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
