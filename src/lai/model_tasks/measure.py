"""Aggregate synthetic task measurements; never persist prompts or model replies."""

import argparse
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from lai.corpus.models import Contract, digest
from lai.model_tasks.contracts import COMPLETION, Completion, TaskRequest
from lai.model_tasks.local import InferenceBudget, LlamaCppBackend, ModelManifest
from lai.model_tasks.prompts import PROMPT_VERSION
from lai.model_tasks.service import BoundedModel, CompletionBackend


class MeasurementCase(Contract):
    request: TaskRequest
    expected: Completion | None


class MeasurementDataset(Contract):
    schema_version: Literal["1"] = "1"
    kind: Literal["synthetic"] = "synthetic"
    review_status: Literal["UNREVIEWED", "LANGUAGE_REVIEWED"] = "UNREVIEWED"
    review_evidence_ref: str | None = Field(default=None, min_length=1, max_length=200)
    cases: tuple[MeasurementCase, ...] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def review_binding(self) -> Self:
        if (self.review_status == "LANGUAGE_REVIEWED") != (self.review_evidence_ref is not None):
            raise ValueError("review_evidence_required_only_when_reviewed")
        if any(
            case.expected is not None and case.expected.task != case.request.task
            for case in self.cases
        ):
            raise ValueError("wrong_expected_task")
        return self


class ReplayBackend:
    """Copies synthetic labels. Demonstrates plumbing only; accuracy is meaningless."""

    def __init__(self) -> None:
        self.response = b"{}"

    def complete(self, prompt: str, schema: dict[str, object]) -> bytes:
        return self.response


def percentile(values: list[float], percentile: float) -> float:
    return sorted(values)[max(0, math.ceil(len(values) * percentile) - 1)]


def measure(
    dataset: MeasurementDataset,
    backend: CompletionBackend,
    repetitions: int = 1,
) -> dict[str, object]:
    dataset = MeasurementDataset.model_validate_json(dataset.model_dump_json())
    if not 1 <= repetitions <= 5:
        raise ValueError("repetitions_out_of_bounds")
    fake = isinstance(backend, ReplayBackend)
    service = BoundedModel(backend)
    groups: dict[tuple[str, str], dict[str, int]] = {}
    latencies: list[float] = []
    peak_ram = 0
    peak_gpu: int | None = None
    for _ in range(repetitions):
        for case in dataset.cases:
            if isinstance(backend, ReplayBackend):
                backend.response = (
                    COMPLETION.dump_json(case.expected) if case.expected is not None else b"{}"
                )
            started = time.monotonic()
            outcome = service.run(case.request.model_dump(mode="python"))
            latencies.append((time.monotonic() - started) * 1000)
            key = (case.request.task, case.request.scenario.language)
            group = groups.setdefault(
                key,
                {
                    "cases": 0,
                    "validated": 0,
                    "fallback": 0,
                    "blocked": 0,
                    "exact_match": 0,
                },
            )
            group["cases"] += 1
            group[outcome.status] += 1
            group["exact_match"] += (
                outcome.output == case.expected
                if case.expected is not None
                else outcome.status == "blocked"
            )
            if isinstance(backend, LlamaCppBackend):
                peak_ram = max(peak_ram, backend.peak_process_ram_mib)
                if backend.peak_total_gpu_mib is not None:
                    peak_gpu = max(peak_gpu or 0, backend.peak_total_gpu_mib)
    report: dict[str, object] = {
        "schema_version": "1",
        "dataset_kind": "synthetic",
        "dataset_sha256": digest(dataset.model_dump_json().encode()),
        "review_status": dataset.review_status,
        "backend_kind": "fake" if fake else "local",
        "prompt_version": PROMPT_VERSION,
        "runs": len(latencies),
        "repetitions": repetitions,
        "groups": [
            {"task": key[0], "language": key[1], **value} for key, value in sorted(groups.items())
        ],
        "latency_ms": {
            "p50": round(statistics.median(latencies), 3),
            "p95": round(percentile(latencies, 0.95), 3),
            "max": round(max(latencies), 3),
        },
        "sampled_peak_process_ram_mib": None if fake else peak_ram,
        "sampled_peak_total_gpu_mib": peak_gpu,
        "resource_fit": "UNVERIFIED",
        "sinhala_capability": "UNVERIFIED",
        "legal_validation": "UNVERIFIED",
        "product_enabled": False,
    }
    if isinstance(backend, LlamaCppBackend):
        report.update(
            {
                "model_sha256": backend.manifest.model_sha256,
                "executable_sha256": backend.manifest.executable_sha256,
                "model_revision": backend.manifest.revision,
                "runner_revision": backend.manifest.runner_revision,
                "budget": backend.budget.model_dump(mode="json"),
                "mode": "gpu" if backend.budget.gpu_layers else "cpu",
            }
        )
    return report


def write_report(path: Path, report: dict[str, object]) -> None:
    # Results stay in ignored local storage and cannot overwrite any existing file.
    path = path.absolute()
    if path.parent.name != ".local" or path.parent.is_symlink():
        raise ValueError("report_requires_direct_local_directory")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("fake", "cpu", "gpu"), default="fake")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--repetitions", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.dataset.stat().st_size > 100_000:
            raise ValueError("dataset_too_large")
        dataset = MeasurementDataset.model_validate_json(args.dataset.read_bytes())
        backend: CompletionBackend
        if args.mode == "fake":
            if args.manifest or args.model or args.executable:
                raise ValueError("fake_mode_has_no_model")
            backend = ReplayBackend()
        else:
            if args.manifest is None or args.model is None or args.executable is None:
                raise ValueError("local_artefacts_required")
            if args.manifest.stat().st_size > 8192:
                raise ValueError("manifest_too_large")
            manifest = ModelManifest.model_validate_json(args.manifest.read_bytes())
            backend = LlamaCppBackend(
                args.executable,
                args.model,
                manifest,
                InferenceBudget(gpu_layers=8 if args.mode == "gpu" else 0),
            )
        write_report(args.output, measure(dataset, backend, args.repetitions))
    except (OSError, ValueError, RuntimeError):
        raise SystemExit(
            "Measurement failed; check local artefacts, dataset and output path"
        ) from None
    print("Aggregate synthetic report written; language quality, fit and launch remain UNVERIFIED")


if __name__ == "__main__":
    main()
