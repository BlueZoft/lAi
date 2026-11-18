"""Content-free runtime logs and bounded, in-memory operational counters."""

import json
import logging
from threading import Lock

ROUTES = ("answer", "health", "assets", "ui", "metrics", "other")
STATUSES = ("2xx", "3xx", "4xx", "5xx", "other")
BUCKETS = (0.05, 0.25, 1.0, 5.0, 30.0)


class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Never call getMessage, interpolate args, inspect request extras or format exceptions.
        event = getattr(record, "event_code", None)
        if type(event) is not str or event not in {
            "runtime_started",
            "runtime_stopped",
            "runtime_failed",
        }:
            event = "runtime_event"
        level = "error" if record.levelno >= logging.ERROR else "info"
        return json.dumps({"event": event, "level": level}, separators=(",", ":"))


def configure_logging() -> None:
    logging.raiseExceptions = False
    handler = logging.StreamHandler()
    handler.setFormatter(SafeFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.INFO)
    for name in tuple(logging.root.manager.loggerDict):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
    logging.getLogger("uvicorn.access").disabled = True


def route_group(path: str) -> str:
    if path == "/api/answers":
        return "answer"
    if path == "/health":
        return "health"
    if path == "/metrics":
        return "metrics"
    if path in {"/assets/app.css", "/assets/app.js", "/assets/labels.json"}:
        return "assets"
    return "ui" if path == "/" else "other"


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counts = {(route, status): 0 for route in ROUTES for status in STATUSES}
        self._buckets = dict.fromkeys(BUCKETS, 0)
        self._total = 0

    def observe(self, route: str, status: int, seconds: float) -> None:
        # Caller-supplied strings can never become a label or create a new time series.
        route = route if route in ROUTES else "other"
        group = f"{status // 100}xx" if 200 <= status <= 599 else "other"
        if route == "metrics":
            return
        with self._lock:
            self._counts[route, group] += 1
            self._total += 1
            for upper in BUCKETS:
                self._buckets[upper] += 0 <= seconds <= upper

    def render(self) -> str:
        with self._lock:
            lines = ["# TYPE lai_http_requests_total counter"]
            lines.extend(
                f'lai_http_requests_total{{route="{route}",status="{status}"}} {count}'
                for (route, status), count in sorted(self._counts.items())
            )
            lines.append("# TYPE lai_http_duration_seconds histogram")
            lines.extend(
                f'lai_http_duration_seconds_bucket{{le="{upper}"}} {count}'
                for upper, count in self._buckets.items()
            )
            lines.extend(
                [
                    f'lai_http_duration_seconds_bucket{{le="+Inf"}} {self._total}',
                    f"lai_http_duration_seconds_count {self._total}",
                ]
            )
        return "\n".join(lines) + "\n"
