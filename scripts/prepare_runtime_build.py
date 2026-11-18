"""Explicit installation stage: download locked public wheels, then build offline."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    target = ROOT / ".local/operations-build"
    if target.is_symlink() or target.parent.is_symlink():
        raise SystemExit("Runtime build directory must not be a symlink")
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    for name in ("wheels", "app"):
        path = target / name
        if path.is_symlink():
            raise SystemExit("Runtime build subdirectory must not be a symlink")
        path.mkdir(mode=0o700, exist_ok=True)
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(ROOT / ".local/uv-cache")
    commands = [
        [
            "uv",
            "export",
            "--frozen",
            "--no-dev",
            "--no-emit-project",
            "--format",
            "requirements-txt",
            "--output-file",
            str(target / "requirements.txt"),
        ],
        [
            str(Path(sys.base_prefix) / "bin/python3"),
            "-m",
            "pip",
            "download",
            "--quiet",
            "--require-hashes",
            "--only-binary=:all:",
            "--dest",
            str(target / "wheels"),
            "--requirement",
            str(target / "requirements.txt"),
        ],
        ["uv", "build", "--wheel", "--offline", "--out-dir", str(target / "app")],
    ]
    for command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=300)
        except (OSError, subprocess.SubprocessError):
            raise SystemExit("Runtime build needs uv and base-interpreter pip") from None
        if result.returncode:
            raise SystemExit("Runtime installation preparation failed; no runtime network enabled")
    print("Locked wheelhouse and application wheel prepared outside Git")


if __name__ == "__main__":
    main()
