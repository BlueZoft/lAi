import stat
import traceback
from pathlib import Path

import psycopg
import pytest

from lai.retrieval.postgres import Connection, connect_local


def test_connection_errors_never_put_password_in_driver_arguments_or_tracebacks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    password_file = tmp_path / "synthetic-password"
    password_file.write_text("SYNTHETIC_AUTH_SENTINEL\n")
    seen: list[Path] = []

    def unavailable(**kwargs: object) -> Connection:
        assert "password" not in kwargs
        path = Path(str(kwargs["passfile"]))
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert path.read_text().endswith(":SYNTHETIC_AUTH_SENTINEL\n")
        seen.append(path)
        raise psycopg.OperationalError("synthetic connection failure")

    monkeypatch.setattr(psycopg, "connect", unavailable)
    with pytest.raises(ValueError, match="local_database_unavailable") as error:
        connect_local(password_file)
    trace = "".join(traceback.format_exception(error.value))
    assert "SYNTHETIC_AUTH_SENTINEL" not in trace
    assert error.value.__suppress_context__ is True
    assert seen and not seen[0].exists()
