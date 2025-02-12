from __future__ import annotations

import unittest
from unittest.mock import patch, sentinel

from maie.core.config import Settings
from maie.demo.server import create_demo_server


class DemoServerTests(unittest.TestCase):
    def test_demo_server_factory_builds_threading_http_server(self) -> None:
        with patch("maie.demo.server.ThreadingHTTPServer", return_value=sentinel.server) as mock_server:
            server = create_demo_server(
                host="127.0.0.1",
                port=8090,
                settings=Settings(enable_telemetry=False),
            )

        self.assertIs(server, sentinel.server)
        self.assertEqual(mock_server.call_args[0][0], ("127.0.0.1", 8090))


if __name__ == "__main__":
    unittest.main()
