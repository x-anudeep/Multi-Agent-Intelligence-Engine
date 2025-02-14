from __future__ import annotations

import argparse

from maie.core.config import Settings
from maie.demo.server import create_demo_server


def main() -> None:
    settings = Settings.from_env()
    parser = argparse.ArgumentParser(
        description="Run the Multi-Agent Intelligence Engine live demo.",
    )
    parser.add_argument("--host", default=settings.demo_host)
    parser.add_argument("--port", type=int, default=settings.demo_port)
    args = parser.parse_args()

    server = create_demo_server(host=args.host, port=args.port, settings=settings)
    url_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    print(f"Live demo running at http://{url_host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
