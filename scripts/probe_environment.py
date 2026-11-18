"""Report non-identifying hardware and tool availability without external requests."""

import json
import os
import platform
import shutil
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    disk = shutil.disk_usage(root)
    memory = Path("/proc/meminfo")
    print("Python:", sys.version.replace("\n", " "))
    print("Platform:", platform.system(), platform.machine())
    print("CPU logical:", os.cpu_count())
    if memory.exists():
        print(
            next(line for line in memory.read_text().splitlines() if line.startswith("MemTotal:"))
        )
    for name in ("cpu.max", "memory.max"):
        path = Path("/sys/fs/cgroup") / name
        print(f"Cgroup {name}:", path.read_text().strip() if path.exists() else "unavailable")
    print("Disk bytes:", json.dumps({"total": disk.total, "used": disk.used, "free": disk.free}))
    print("GPU device nodes:", sorted(str(p) for p in Path("/dev").glob("nvidia*")))
    print("DRI device nodes:", sorted(str(p) for p in Path("/dev").glob("dri/*")))
    print(
        "Tool paths:",
        json.dumps(
            {
                name: shutil.which(name)
                for name in (
                    "python3.12",
                    "uv",
                    "git",
                    "curl",
                    "docker",
                    "psql",
                    "pg_ctl",
                    "apt-get",
                    "nvidia-smi",
                    "node",
                    "npm",
                    "make",
                    "gh",
                )
            }
        ),
    )


if __name__ == "__main__":
    main()
