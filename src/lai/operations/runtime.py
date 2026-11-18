"""Unix-socket-only entry point for the isolated laptop image."""

import argparse
import logging
import os
from pathlib import Path

import uvicorn

from lai.operations.privacy import configure_logging


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loopback", action="store_true", help="Host development; not isolated")
    parser.add_argument("--host", choices=("127.0.0.1", "::1"), default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Choose an unprivileged local port")
    configure_logging()
    logger = logging.getLogger("lai.runtime")
    socket = Path("/run/lai-api/http.sock")
    if not args.loopback and socket.exists():
        raise SystemExit("runtime_socket_exists; inspect the stopped instance before removal")
    os.umask(0o007)
    logger.info("", extra={"event_code": "runtime_started"})
    try:
        uvicorn.run(
            "lai.api:app",
            uds=None if args.loopback else str(socket),
            host=args.host,
            port=args.port,
            access_log=False,
            log_config=None,
            proxy_headers=False,
            server_header=False,
            timeout_keep_alive=5,
            limit_concurrency=32,
            limit_max_requests=1000,
        )
    except Exception:
        logger.error("", extra={"event_code": "runtime_failed"})
        raise SystemExit(1) from None
    finally:
        logger.info("", extra={"event_code": "runtime_stopped"})


if __name__ == "__main__":
    main()
