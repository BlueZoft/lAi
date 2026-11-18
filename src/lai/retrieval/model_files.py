"""Streaming integrity checks for local embedding-model snapshots."""

import hashlib
import json
from pathlib import Path


def file_digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def verify_model_files(root: Path, revision: str) -> None:
    manifest = root / "lai-model-manifest.json"
    if not manifest.exists():
        return
    data = json.loads(manifest.read_bytes())
    if data.get("revision") != revision or not data.get("files"):
        raise ValueError("model_manifest_invalid")
    for name, expected in data["files"].items():
        path = (root / name).resolve()
        if (
            not path.is_relative_to(root.resolve())
            or not path.is_file()
            or file_digest(path) != expected
        ):
            raise ValueError("model_file_checksum_mismatch")
