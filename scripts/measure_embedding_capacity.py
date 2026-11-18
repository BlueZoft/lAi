"""Laptop CPU capacity probe on three invented strings; no legal recall measurement.

Run this process to completion before instruct-model measurements. It never loads
the instruct model. Optional model dependencies and a verified local BGE snapshot
are required; no automatic acquisition occurs.
"""

import argparse
import os
import resource
import time
from pathlib import Path

from lai.corpus.models import digest
from lai.model_tasks.measure import write_report
from lai.retrieval.embeddings import load_local_bge


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["OMP_NUM_THREADS"] = "2"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    try:
        manifest = args.model_path / "lai-model-manifest.json"
        if not manifest.is_file():
            raise ValueError("verified_snapshot_manifest_required")
        started = time.monotonic()
        backend = load_local_bge(args.model_path, args.revision, "cpu")
        embeddings = backend.embed(["SYNTHETIC documents", "ලේඛන පෝරම", "ஆவணங்கள் படிவம்"])
        elapsed = (time.monotonic() - started) * 1000
        report = {
            "schema_version": "1",
            "backend_kind": "bge_m3",
            "device": "cpu",
            "dataset_kind": "synthetic",
            "strings": len(embeddings),
            "manifest_sha256": digest(manifest.read_bytes()),
            "peak_process_ram_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
            "cold_load_and_encode_ms": round(elapsed, 3),
            "legal_validation": "UNVERIFIED",
            "resource_fit": "UNVERIFIED",
        }
        write_report(args.output, report)
    except Exception:
        raise SystemExit(
            "Embedding probe failed; inspect local snapshot and model installation"
        ) from None
    print("Synthetic CPU report written; process exit releases embedding residency")


if __name__ == "__main__":
    main()
