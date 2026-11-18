import io
import logging
from datetime import UTC, datetime
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from lai.api import create_app
from lai.operations.backup import crypt
from lai.operations.prepare import prepare
from lai.operations.privacy import Metrics, SafeFormatter
from lai.operations.retention import PrivacyPolicy, expired_files, initialise_retention

pytestmark = pytest.mark.safety


def test_safe_formatter_never_formats_input_arguments_exceptions_or_extras() -> None:
    class Hostile:
        def __str__(self) -> str:
            raise AssertionError("must not inspect private content")

    record = logging.LogRecord(
        "arbitrary", logging.ERROR, "private/path", 1, "SYNTHETIC_PRIVATE %s", (Hostile(),), None
    )
    record.private_query = "SYNTHETIC_PRIVATE"
    record.event_code = "SYNTHETIC_PRIVATE"
    assert SafeFormatter().format(record) == '{"event":"runtime_event","level":"error"}'
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(SafeFormatter())
    try:
        raise ValueError("SYNTHETIC_PRIVATE")
    except ValueError:
        import sys

        record.exc_info = sys.exc_info()
    handler.handle(record)
    assert "SYNTHETIC" not in stream.getvalue()
    assert "Traceback" not in stream.getvalue()


def test_metrics_cannot_grow_labels_from_input() -> None:
    metrics = Metrics()
    before = len(metrics.render().splitlines())
    for _ in range(100):
        metrics.observe("SYNTHETIC_PRIVATE", 404, 0.1)
    text = metrics.render()
    assert "SYNTHETIC" not in text and len(text.splitlines()) == before
    assert 'route="other",status="4xx"} 100' in text


def test_real_api_metrics_errors_and_cookies_do_not_expose_private_input() -> None:
    client = TestClient(create_app())
    canary = "SYNTHETIC_PRIVATE_T7"
    response = client.post("/api/answers", json={"scenario": {"text": canary + " documents"}})
    assert response.json()["status"] == "review_required"
    assert canary not in response.text and "set-cookie" not in response.headers
    client.get("/" + canary + "?" + canary)
    metrics = client.get("/metrics?" + canary)
    assert canary not in metrics.text and "lai_http_requests_total" in metrics.text
    assert metrics.headers["cache-control"] == "no-store"
    # A fresh process/application has no prior session/query/counter state.
    fresh = TestClient(create_app()).get("/metrics").text
    assert 'route="answer",status="2xx"} 0' in fresh


def test_operations_prepare_is_private_and_preserves_credentials(tmp_path: Path) -> None:
    root = tmp_path / "operations"
    prepare(root)
    original = (root / "postgres.password").read_bytes()
    assert root.stat().st_mode & 0o777 == 0o700
    assert (root / "backup.passphrase").stat().st_mode & 0o777 == 0o600
    prepare(root)
    assert (root / "postgres.password").read_bytes() == original
    (root / "postgres.password").chmod(0o644)
    with pytest.raises(ValueError):
        prepare(root)


def test_retention_uses_owned_timestamps_and_leaves_unexpired_files(tmp_path: Path) -> None:
    root = tmp_path / "retained"
    initialise_retention(root)
    old = root / "reports/20261101T000000Z-aaaaaaaa.json"
    fresh = root / "backups/20261118T000000Z-bbbbbbbb.gpg"
    old.write_text("SYNTHETIC aggregate")
    fresh.write_text("SYNTHETIC encrypted stand-in")
    now = datetime(2026, 11, 19, tzinfo=UTC)
    assert expired_files(root, now, PrivacyPolicy()) == (old,)
    assert old.exists()  # Preview is read-only.
    for path in expired_files(root, now, PrivacyPolicy()):
        path.unlink()
    assert fresh.exists() and not old.exists()


@pytest.mark.parametrize("kind", ["unknown", "symlink", "directory"])
def test_retention_fails_closed_before_deleting_unowned_paths(tmp_path: Path, kind: str) -> None:
    root = tmp_path / "retained"
    initialise_retention(root)
    old = root / "reports/20261101T000000Z-aaaaaaaa.json"
    old.write_text("SYNTHETIC")
    target = root / "reports/unowned"
    if kind == "unknown":
        target.write_text("not managed")
    elif kind == "symlink":
        target.symlink_to(old)
    else:
        target.mkdir()
    with pytest.raises(ValueError):
        expired_files(root, datetime(2026, 11, 19, tzinfo=UTC), PrivacyPolicy())
    assert old.exists()


def test_retention_requires_marker_and_refuses_symlink_root(tmp_path: Path) -> None:
    root = tmp_path / "retained"
    root.mkdir()
    with pytest.raises(OSError):
        expired_files(root, datetime.now(UTC), PrivacyPolicy())
    link = tmp_path / "link"
    link.symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError):
        initialise_retention(link)


def test_no_query_storage_policy_cannot_be_relaxed() -> None:
    with pytest.raises(ValueError):
        PrivacyPolicy(server_query_persistence=True)  # type: ignore[arg-type]


@pytest.mark.parametrize("crypto_code, cleanup_code", [(0, 0), (2, 0), (0, 1)])
def test_backup_errors_are_fixed_and_owned_agent_cleanup_is_required(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    crypto_code: int,
    cleanup_code: int,
) -> None:
    password = tmp_path / "passphrase"
    password.write_text("SYNTHETIC_PRIVATE_PASSPHRASE_1234567890")
    password.chmod(0o600)
    runner = Mock(
        side_effect=[
            CompletedProcess(
                [], crypto_code, stdout=b"SYNTHETIC encrypted", stderr=b"SYNTHETIC_PRIVATE"
            ),
            CompletedProcess([], cleanup_code, stdout=b"", stderr=b""),
        ]
    )
    monkeypatch.setattr("lai.operations.backup.subprocess.run", runner)
    if crypto_code or cleanup_code:
        with pytest.raises(RuntimeError) as caught:
            crypt(b"SYNTHETIC plaintext", password, tmp_path / "gpg")
        assert "SYNTHETIC_PRIVATE" not in str(caught.value)
    else:
        assert crypt(b"SYNTHETIC plaintext", password, tmp_path / "gpg") == b"SYNTHETIC encrypted"
    assert runner.call_count == 2
    assert "SYNTHETIC_PRIVATE" not in str(runner.call_args_list[0].args)
    assert runner.call_args_list[1].args[0][-2:] == ["--kill", "gpg-agent"]
