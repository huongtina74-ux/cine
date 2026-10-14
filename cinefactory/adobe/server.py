from __future__ import annotations

import argparse
import signal
import threading
from pathlib import Path

from .bridge import AdobeBridgeServer


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CineFactory authenticated loopback bridge for Adobe UXP plugins."
    )
    parser.add_argument(
        "--root",
        default="data/studio/adobe_bridge",
        help="Bridge state directory relative to the current working directory.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8791)
    args = parser.parse_args()

    server = AdobeBridgeServer(
        root=Path(args.root),
        host=args.host,
        port=args.port,
    ).start()
    print(
        f"CineFactory Adobe bridge listening on {server.base_url}",
        flush=True,
    )

    stopped = threading.Event()

    def stop_handler(*_):
        stopped.set()

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    try:
        while not stopped.wait(1.0):
            pass
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
