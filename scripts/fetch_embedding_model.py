"""Explicit online acquisition for TARGET B. User queries are never inputs."""

import argparse
import importlib
import json
import sys
from pathlib import Path

from lai.retrieval.model_files import file_digest, verify_model_files

MODEL = "BAAI/bge-m3"
ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "models/bge-m3")
    args = parser.parse_args()
    try:
        destination = args.output.resolve()
        if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "models"):
            raise ValueError("model_output_must_be_ignored")
        hub = importlib.import_module("huggingface_hub")
        info = hub.model_info(MODEL, revision=args.revision, files_metadata=True)
        revision = str(info.sha)
        if len(revision) != 40 or any(
            character not in "0123456789abcdef" for character in revision
        ):
            raise ValueError("model_revision_invalid")
        directory = destination / revision
        verify_model_files(directory, revision)
        hub.snapshot_download(
            repo_id=MODEL,
            revision=revision,
            local_dir=str(directory),
            allow_patterns=[
                "*.json",
                "*.txt",
                "*.model",
                "*.safetensors",
                "*.bin",
                "*.pt",
                "README.md",
                "LICENSE*",
                "NOTICE*",
            ],
            ignore_patterns=["onnx/*", "imgs/*"],
        )
        for entry in info.siblings:
            lfs = getattr(entry, "lfs", None)
            expected = lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)
            path = (directory / entry.rfilename).resolve()
            if not path.is_relative_to(directory.resolve()):
                raise ValueError("model_path_invalid")
            if path.is_file() and expected and file_digest(path) != expected:
                raise ValueError("publisher_checksum_mismatch")
        checksums = {
            str(path.relative_to(directory)): file_digest(path)
            for path in directory.rglob("*")
            if path.is_file()
            and ".cache" not in path.relative_to(directory).parts
            and path.name != "lai-model-manifest.json"
        }
        (directory / "lai-model-manifest.json").write_text(
            json.dumps({"model": MODEL, "revision": revision, "files": checksums}, indent=2) + "\n"
        )
        verify_model_files(directory, revision)
    except Exception:
        print(json.dumps({"error": "model_acquisition_failed"}), file=sys.stderr)
        return 2
    print(json.dumps({"model": MODEL, "revision": revision, "verified_files": len(checksums)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
