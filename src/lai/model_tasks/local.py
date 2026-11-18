"""One-shot llama.cpp adapter with pinned local artefacts and bounded process I/O.

No server, downloads, shell or user-content arguments. This is not an OS network sandbox.
"""

import os
import selectors
import signal
import subprocess
import time
from contextlib import suppress
from pathlib import Path
from typing import Literal

from pydantic import Field

from lai.corpus.models import Contract, Sha256
from lai.retrieval.model_files import file_digest


class ModelManifest(Contract):
    schema_version: Literal["1"] = "1"
    model_id: str = Field(min_length=1, max_length=200)
    revision: str = Field(min_length=1, max_length=200)
    runner_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    model_sha256: Sha256
    executable_sha256: Sha256
    quantisation: Literal["Q4_K_M"] = "Q4_K_M"
    parameters_billions: float = Field(ge=3.0, le=4.5)
    licence_evidence_ref: str = Field(min_length=1, max_length=200)
    # These fields record operator assertions; a hash does not validate architecture/licensing.


class InferenceBudget(Contract):
    context_tokens: Literal[2048] = 2048
    output_tokens: Literal[256] = 256
    threads: Literal[2] = 2
    gpu_layers: Literal[0, 8] = 0
    timeout_seconds: float = Field(default=120.0, ge=0.05, le=120.0)
    output_bytes: Literal[8192] = 8192
    minimum_available_ram_mib: Literal[6144] = 6144
    model_file_limit_mib: Literal[3072] = 3072
    process_ram_target_mib: Literal[8192] = 8192
    total_gpu_target_mib: Literal[3072] = 3072


def available_ram_mib() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    raise RuntimeError("memory_measurement_unavailable")


def process_ram_mib(pid: int) -> int:
    try:
        lines = Path(f"/proc/{pid}/status").read_text().splitlines()
        return max(
            (
                int(line.split()[1]) // 1024
                for line in lines
                if line.startswith(("VmHWM:", "VmRSS:"))
            ),
            default=0,
        )
    except FileNotFoundError:
        return 0


def gpu_memory_mib() -> int | None:
    """Total device-0 usage, including other applications. No query or model text."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--id=0", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            timeout=2,
            check=True,
        )
        return int(result.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


class LlamaCppBackend:
    def __init__(
        self,
        executable: Path,
        model: Path,
        manifest: ModelManifest,
        budget: InferenceBudget | None = None,
    ):
        self.executable, self.model = executable.resolve(), model.resolve()
        self.budget = InferenceBudget.model_validate_json(
            (budget or InferenceBudget()).model_dump_json()
        )
        self.manifest = ModelManifest.model_validate_json(manifest.model_dump_json())
        if (
            not self.executable.is_file()
            or not os.access(self.executable, os.X_OK)
            or not self.model.is_file()
            or self.model.stat().st_size == 0
            or self.model.stat().st_size > self.budget.model_file_limit_mib * 1024**2
            or file_digest(self.model) != manifest.model_sha256
            or file_digest(self.executable) != manifest.executable_sha256
        ):
            raise ValueError("local_model_integrity_failed")
        self.peak_process_ram_mib = 0
        self.peak_total_gpu_mib: int | None = None

    def complete(self, prompt: str, schema: dict[str, object]) -> bytes:
        import json

        if len(prompt.encode("utf-8")) > 16384:
            raise ValueError("prompt_too_large")
        if available_ram_mib() < self.budget.minimum_available_ram_mib:
            raise RuntimeError("insufficient_available_ram")
        self.peak_process_ram_mib = 0
        self.peak_total_gpu_mib = None
        if self.budget.gpu_layers:
            before = gpu_memory_mib()
            if before is None or before >= self.budget.total_gpu_target_mib:
                raise RuntimeError("gpu_unavailable_or_busy")
            self.peak_total_gpu_mib = before
        # Check integrity at each invocation; files must remain immutable during the run.
        if file_digest(self.model) != self.manifest.model_sha256 or (
            file_digest(self.executable) != self.manifest.executable_sha256
        ):
            raise ValueError("local_model_integrity_failed")
        command = [
            str(self.executable),
            "-m",
            str(self.model),
            "-f",
            "/dev/stdin",
            "--no-display-prompt",
            "--simple-io",
            "--log-disable",
            "--no-perf",
            "--no-conversation",
            "--no-context-shift",
            "--no-warmup",
            "--temp",
            "0",
            "--seed",
            "0",
            "-c",
            str(self.budget.context_tokens),
            "-n",
            str(self.budget.output_tokens),
            "-t",
            str(self.budget.threads),
            "-ngl",
            str(self.budget.gpu_layers),
            "-j",
            json.dumps(schema),
        ]
        # Do not pass application credentials, proxy settings or model-download tokens.
        environment = {
            "PATH": os.defpath,
            "LANG": "C.UTF-8",
            "CUDA_VISIBLE_DEVICES": "0" if self.budget.gpu_layers else "",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "GGML_CUDA_ENABLE_UNIFIED_MEMORY": "0",
            "OMP_NUM_THREADS": "2",
        }
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=environment,
            start_new_session=True,
        )
        started = time.monotonic()
        output = bytearray()
        next_gpu_check = started
        try:
            self.peak_process_ram_mib = process_ram_mib(process.pid)
            assert process.stdin is not None and process.stdout is not None
            # Non-blocking writes are also deadline-bound if a broken runner never reads stdin.
            os.set_blocking(process.stdin.fileno(), False)
            pending = memoryview(prompt.encode("utf-8"))
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdin, selectors.EVENT_WRITE, "input")
                selector.register(process.stdout, selectors.EVENT_READ, "output")
                while selector.get_map():
                    if time.monotonic() - started > self.budget.timeout_seconds:
                        raise TimeoutError("local_model_timeout")
                    self.peak_process_ram_mib = max(
                        self.peak_process_ram_mib, process_ram_mib(process.pid)
                    )
                    if self.peak_process_ram_mib > self.budget.process_ram_target_mib:
                        raise RuntimeError("process_ram_budget_exceeded")
                    if self.budget.gpu_layers and time.monotonic() >= next_gpu_check:
                        used = gpu_memory_mib()
                        if used is None or used > self.budget.total_gpu_target_mib:
                            raise RuntimeError("gpu_budget_exceeded_or_unmeasurable")
                        self.peak_total_gpu_mib = max(self.peak_total_gpu_mib or 0, used)
                        next_gpu_check = time.monotonic() + 0.5
                    for key, _ in selector.select(timeout=0.05):
                        if key.data == "input":
                            try:
                                written = os.write(process.stdin.fileno(), pending)
                                pending = pending[written:]
                            except BrokenPipeError:
                                raise RuntimeError("local_model_stdin_closed") from None
                            if not pending:
                                selector.unregister(process.stdin)
                                process.stdin.close()
                        else:
                            block = os.read(process.stdout.fileno(), 4096)
                            if not block:
                                selector.unregister(process.stdout)
                            else:
                                output.extend(block)
                                if len(output) > self.budget.output_bytes:
                                    raise ValueError("local_model_output_limit")
                remaining = self.budget.timeout_seconds - (time.monotonic() - started)
                process.wait(timeout=max(0.001, remaining))
                if process.returncode != 0:
                    raise RuntimeError("local_model_failed")
        finally:
            # Kill the owned process group on both success and failure, then reap the direct child.
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            if process.stdin is not None:
                process.stdin.close()
            if process.stdout is not None:
                process.stdout.close()
        return bytes(output).strip()
