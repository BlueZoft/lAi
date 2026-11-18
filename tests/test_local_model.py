"""Exercise real process boundaries using a tiny stand-in, never model inference."""

import json
import os
import time
from pathlib import Path

import pytest

from lai.corpus.models import digest
from lai.model_tasks.local import InferenceBudget, LlamaCppBackend, ModelManifest
from lai.model_tasks.pin import main as pin_main
from lai.retrieval.model_files import file_digest

pytestmark = pytest.mark.safety


@pytest.fixture(autouse=True)
def synthetic_available_ram(monkeypatch: pytest.MonkeyPatch) -> None:
    # Unit process tests must not depend on the CI runner's installed/free RAM.
    monkeypatch.setattr("lai.model_tasks.local.available_ram_mib", lambda: 10000)


def stand_in(tmp_path: Path, code: str) -> LlamaCppBackend:
    executable = tmp_path / "synthetic-runner"
    executable.write_text("#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\n" + code)
    executable.chmod(0o700)
    model = tmp_path / "synthetic-model"
    model.write_text("SYNTHETIC stand-in, not a model")
    manifest = ModelManifest(
        model_id="SYNTHETIC",
        revision="synthetic-v1",
        runner_revision="0" * 40,
        model_sha256=file_digest(model),
        executable_sha256=file_digest(executable),
        parameters_billions=4.0,
        licence_evidence_ref="synthetic-test-only",
    )
    return LlamaCppBackend(executable, model, manifest)


def test_pinned_runner_receives_stdin_not_sensitive_arguments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SYNTHETIC_APPLICATION_SECRET", "synthetic-test-value")
    backend = stand_in(
        tmp_path,
        "import json, os\nprint(json.dumps({'args':sys.argv,"
        "'cuda':os.environ['CUDA_VISIBLE_DEVICES'],"
        "'secret_present':'SYNTHETIC_APPLICATION_SECRET' in os.environ}))\n",
    )
    result = json.loads(backend.complete("SYNTHETIC PRIVATE INPUT", {"type": "object"}))
    assert "SYNTHETIC PRIVATE INPUT" not in json.dumps(result["args"])
    assert result["cuda"] == ""
    assert not result["secret_present"]
    assert result["args"][result["args"].index("-ngl") + 1] == "0"
    assert "--no-context-shift" in result["args"]
    assert backend.peak_process_ram_mib >= 0


@pytest.mark.parametrize("artefact", ["model", "executable"])
def test_pins_are_rechecked_before_each_invocation(tmp_path: Path, artefact: str) -> None:
    backend = stand_in(tmp_path, "print('{}')\n")
    path = getattr(backend, artefact)
    path.write_text("SYNTHETIC changed")
    with pytest.raises(ValueError, match="integrity"):
        backend.complete("SYNTHETIC", {})


def test_wrong_manifest_and_missing_files_rejected(tmp_path: Path) -> None:
    backend = stand_in(tmp_path, "print('{}')\n")
    wrong = backend.manifest.model_copy(update={"model_sha256": digest(b"different")})
    with pytest.raises(ValueError, match="integrity"):
        LlamaCppBackend(backend.executable, backend.model, wrong)
    backend.model.unlink()
    with pytest.raises(ValueError, match="integrity"):
        LlamaCppBackend(backend.executable, backend.model, backend.manifest)


@pytest.mark.parametrize(
    "code",
    [
        "print('x' * 9000)\n",
        "sys.exit(3)\n",
        "import time\ntime.sleep(10)\n",
    ],
)
def test_failure_timeout_and_flood_are_bounded(tmp_path: Path, code: str) -> None:
    backend = stand_in(tmp_path, code)
    backend.budget = InferenceBudget(timeout_seconds=0.2)
    with pytest.raises((ValueError, RuntimeError, TimeoutError)):
        backend.complete("SYNTHETIC", {})
    # A new invocation proves owned child/pipe cleanup allows recovery.
    healthy = stand_in(tmp_path, "print('{}')\n")
    assert healthy.complete("SYNTHETIC", {}) == b"{}"


def test_low_ram_or_unavailable_gpu_does_not_spawn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend = stand_in(tmp_path, "print('{}')\n")
    monkeypatch.setattr("lai.model_tasks.local.available_ram_mib", lambda: 1)
    with pytest.raises(RuntimeError, match="ram"):
        backend.complete("SYNTHETIC", {})
    monkeypatch.setattr("lai.model_tasks.local.available_ram_mib", lambda: 10000)
    monkeypatch.setattr("lai.model_tasks.local.gpu_memory_mib", lambda: None)
    backend.budget = InferenceBudget(gpu_layers=8)
    with pytest.raises(RuntimeError, match="gpu"):
        backend.complete("SYNTHETIC", {})


def test_ram_and_gpu_over_budget_kill_owned_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend = stand_in(tmp_path, "import time\ntime.sleep(10)\n")
    monkeypatch.setattr("lai.model_tasks.local.process_ram_mib", lambda pid: 9000)
    with pytest.raises(RuntimeError, match="ram_budget"):
        backend.complete("SYNTHETIC", {})
    monkeypatch.setattr("lai.model_tasks.local.process_ram_mib", lambda pid: 1)
    calls = iter([0, 3500])
    monkeypatch.setattr("lai.model_tasks.local.gpu_memory_mib", lambda: next(calls))
    backend.budget = InferenceBudget(gpu_layers=8)
    with pytest.raises(RuntimeError, match="gpu_budget"):
        backend.complete("SYNTHETIC", {})


def test_runner_which_never_reads_stdin_is_killed_and_reaped(tmp_path: Path) -> None:
    backend = stand_in(tmp_path, "print('{}')\n")
    marker = tmp_path / "owned-pid"
    backend.executable.write_text(
        "#!/usr/bin/env python3\nimport os, time\nfrom pathlib import Path\n"
        + f"Path({str(marker)!r}).write_text(str(os.getpid()))\ntime.sleep(10)\n"
    )
    manifest = backend.manifest.model_copy(
        update={
            "executable_sha256": file_digest(backend.executable),
        }
    )
    backend = LlamaCppBackend(
        backend.executable, backend.model, manifest, InferenceBudget(timeout_seconds=1.0)
    )
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        backend.complete("x" * 16000, {})
    assert time.monotonic() - started < 5
    pid = int(marker.read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_pinning_helper_checks_trusted_inputs_and_never_overwrites(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    backend = stand_in(tmp_path, "print('{}')\n")
    output = tmp_path / ".local/pins.json"
    args = [
        "pin",
        "--model",
        str(backend.model),
        "--executable",
        str(backend.executable),
        "--model-id",
        "SYNTHETIC",
        "--revision",
        "synthetic-v1",
        "--runner-revision",
        "0" * 40,
        "--parameters-billions",
        "4.0",
        "--licence-evidence-ref",
        "synthetic-only",
        "--output",
        str(output),
        "--expected-model-sha256",
        backend.manifest.model_sha256,
        "--expected-executable-sha256",
        backend.manifest.executable_sha256,
    ]
    monkeypatch.setattr("sys.argv", args)
    pin_main()
    assert output.stat().st_mode & 0o777 == 0o600
    assert ModelManifest.model_validate_json(output.read_bytes()).model_sha256 == (
        backend.manifest.model_sha256
    )
    with pytest.raises(SystemExit, match="Pinning failed"):
        pin_main()
    output.unlink()
    args[args.index("--expected-model-sha256") + 1] = "0" * 64
    with pytest.raises(SystemExit, match="Pinning failed"):
        pin_main()
    assert not output.exists()
    assert str(tmp_path) not in capsys.readouterr().out


def test_initial_telemetry_error_still_reaps_the_owned_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend = stand_in(tmp_path, "import time\ntime.sleep(10)\n")
    pids: list[int] = []

    def failed_probe(pid: int) -> int:
        pids.append(pid)
        raise RuntimeError("synthetic telemetry error")

    monkeypatch.setattr("lai.model_tasks.local.process_ram_mib", failed_probe)
    with pytest.raises(RuntimeError, match="telemetry"):
        backend.complete("SYNTHETIC", {})
    assert len(pids) == 1
    with pytest.raises(ProcessLookupError):
        os.kill(pids[0], 0)
