"""Enforce file categories and size limits for tracked and non-ignored files."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1_000_000
BLOCKED_DIRECTORIES = {
    "data",
    "models",
    "corpus",
    "embeddings",
    "vectorstores",
    "databases",
    "archives",
    "backups",
    ".local",
    ".venv",
}
BLOCKED_SUFFIXES = {
    ".pdf",
    ".onnx",
    ".gguf",
    ".safetensors",
    ".pt",
    ".pth",
    ".npy",
    ".npz",
    ".pkl",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".7z",
    ".whl",
}


def main() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    names = sorted(set(result.stdout.decode().strip("\0").split("\0")) - {""})
    violations: list[str] = []
    for name in names:
        path = ROOT / name
        parts = Path(name).parts
        if (
            path.is_symlink()
            or BLOCKED_DIRECTORIES.intersection(parts)
            or path.suffix.lower() in BLOCKED_SUFFIXES
            or path.name == ".env"
            or path.name.startswith(".env.")
        ):
            violations.append(f"Forbidden artefact: {name}")
            continue
        if path.stat().st_size > MAX_BYTES:
            violations.append(f"File exceeds 1 MB: {name}")
            continue
        content = path.read_bytes()
        if b"\0" in content or (path.name == ".gitattributes" and b"filter=lfs" in content):
            violations.append(f"Binary artefact or LFS configuration: {name}")
        if name.startswith("tests/fixtures/") and len(content) > 10_000:
            violations.append(f"Fixture exceeds synthetic fixture budget: {name}")
    if violations:
        raise SystemExit("\n".join(violations))
    print(f"Repository hygiene passed ({len(names)} files; 1 MB cap)")


if __name__ == "__main__":
    main()
