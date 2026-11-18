"""Validate the normalised standalone laptop Compose configuration, without startup."""

import json
import subprocess

from lai.operations.configuration import validate_runtime


def main() -> None:
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "compose.runtime.yaml", "config", "--format", "json"],
            capture_output=True,
            check=True,
            timeout=20,
        )
        validate_runtime(json.loads(result.stdout))
    except (ValueError, OSError, subprocess.SubprocessError):
        raise SystemExit("Runtime configuration controls failed") from None
    print("Standalone runtime controls valid; no service started")


if __name__ == "__main__":
    main()
