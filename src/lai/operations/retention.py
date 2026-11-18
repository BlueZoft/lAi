"""Delete only old, explicitly named operations artefacts; never corpus/session data."""

import argparse
import os
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import Field

from lai.corpus.models import Contract

MARKER = "lai-operations-v1\n"
NAME = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}\.(?:json|gpg)$")


class PrivacyPolicy(Contract):
    schema_version: Literal["1"] = "1"
    server_query_persistence: Literal[False] = False
    accounts: Literal[False] = False
    browser_storage: Literal[False] = False
    browser_idle_seconds: Literal[300] = 300
    query_logs: Literal[False] = False
    metric_retention_hours: Literal[1] = 1
    report_retention_days: int = Field(default=7, ge=1, le=7)
    encrypted_backup_retention_days: int = Field(default=7, ge=1, le=7)


def initialise_retention(root: Path) -> None:
    if root.is_symlink():
        raise ValueError("symlink_root")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    marker = root / ".lai-operations"
    if marker.exists():
        if marker.is_symlink() or marker.read_text() != MARKER:
            raise ValueError("unrecognised_operations_directory")
    else:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(MARKER)
    for name in ("reports", "backups"):
        path = root / name
        if path.is_symlink():
            raise ValueError("symlink_directory")
        path.mkdir(mode=0o700, exist_ok=True)


def expired_files(root: Path, now: datetime, policy: PrivacyPolicy) -> tuple[Path, ...]:
    marker = root / ".lai-operations"
    if root.is_symlink() or marker.is_symlink() or marker.read_text() != MARKER:
        raise ValueError("unrecognised_operations_directory")
    expired: list[Path] = []
    for name, days in (
        ("reports", policy.report_retention_days),
        ("backups", policy.encrypted_backup_retention_days),
    ):
        directory = root / name
        if directory.is_symlink():
            raise ValueError("symlink_directory")
        for path in directory.iterdir():
            if path.is_symlink() or not path.is_file() or not NAME.fullmatch(path.name):
                raise ValueError("unknown_retention_artefact")
            created = datetime.strptime(path.name[:16], "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
            if created <= now - timedelta(days=days):
                expired.append(path)
    return tuple(sorted(expired))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(".local/operations/retained"))
    parser.add_argument("--apply", action="store_true", help="Default is a non-mutating preview")
    args = parser.parse_args()
    try:
        paths = expired_files(args.root, datetime.now(UTC), PrivacyPolicy())
        if args.apply:
            for path in paths:
                path.unlink()
    except (OSError, ValueError):
        raise SystemExit("Retention stopped; inspect owned artefacts and permissions") from None
    print(f"{'Deleted' if args.apply else 'Would delete'} {len(paths)} expired owned artefacts")


if __name__ == "__main__":
    main()
