"""Synthetic network/Unix-HTTP probes for an isolated namespace, never real queries."""

import argparse
import json
import socket


def no_egress() -> dict[str, bool]:
    checks: dict[str, bool] = {}
    targets = (
        ("ipv4_tcp_blocked", socket.AF_INET, socket.SOCK_STREAM, ("198.51.100.1", 443)),
        ("ipv4_udp_blocked", socket.AF_INET, socket.SOCK_DGRAM, ("198.51.100.1", 53)),
        ("ipv6_tcp_blocked", socket.AF_INET6, socket.SOCK_STREAM, ("2001:db8::1", 443)),
    )
    for label, family, kind, address in targets:
        try:
            with socket.socket(family, kind) as stream:
                stream.settimeout(1)
                if kind == socket.SOCK_DGRAM:
                    stream.sendto(b"SYNTHETIC-EGRESS-PROBE", address)
                else:
                    stream.connect(address)
        except OSError:
            checks[label] = True
        else:
            checks[label] = False
    try:
        socket.getaddrinfo("lai-t7-egress.invalid", 443)
    except OSError:
        checks["dns_blocked"] = True
    else:
        checks["dns_blocked"] = False
    return checks


def unix_http(method: str, path: str, body: bytes = b"") -> tuple[int, bytes]:
    headers = (
        f"{method} {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n"
        f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n"
    ).encode()
    with socket.socket(socket.AF_UNIX) as stream:
        stream.settimeout(5)
        stream.connect("/run/lai-api/http.sock")
        stream.sendall(headers + body)
        response = bytearray()
        while chunk := stream.recv(8192):
            response.extend(chunk)
            if len(response) > 131072:
                raise ValueError("probe_response_too_large")
    head, payload = bytes(response).split(b"\r\n\r\n", 1)
    # JSON responses have Content-Length. Metrics may be chunked and are checked as bytes.
    return int(head.split(b" ", 2)[1]), payload


def http_checks() -> dict[str, bool]:
    canary = "SYNTHETIC_T7_PRIVATE_CANARY"
    status, health = unix_http("GET", "/health")
    post, answer = unix_http(
        "POST",
        "/api/answers",
        json.dumps(
            {
                "scenario": {"text": canary + " documents"},
            }
        ).encode(),
    )
    _, metrics = unix_http("GET", "/metrics?" + canary)
    _, missing = unix_http("GET", "/" + canary)
    return {
        "health_closed": status == 200 and b'"navigator_enabled":false' in health,
        "answer_closed": post == 200 and b'"status":"review_required"' in answer,
        "no_content_echo": canary.encode() not in health + answer + metrics + missing,
        "bounded_metrics": b"lai_http_requests_total" in metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("network", "http"))
    args = parser.parse_args()
    checks = no_egress() if args.kind == "network" else http_checks()
    print(json.dumps(checks, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
