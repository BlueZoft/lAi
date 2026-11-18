"""Create dedicated owner-only operations paths; preserve existing credentials."""

import os
from pathlib import Path
from secrets import token_urlsafe

from lai.operations.retention import initialise_retention


def prepare(root: Path) -> None:
    if root.is_symlink() or root.parent.is_symlink():
        raise ValueError("symlink_operations_root")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    root.chmod(0o700)
    for name in ("api-socket", "db-socket"):
        path = root / name
        if path.is_symlink():
            raise ValueError("symlink_socket_directory")
        path.mkdir(mode=0o770, exist_ok=True)
        path.chmod(0o770)
    for name in ("postgres.password", "backup.passphrase"):
        path = root / name
        if path.exists():
            if path.is_symlink() or path.stat().st_mode & 0o077 or path.stat().st_size < 32:
                raise ValueError("unsafe_operations_credential_file")
            continue
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(token_urlsafe(48) + "\n")
    initialise_retention(root / "retained")


def main() -> None:
    try:
        prepare(Path(".local/operations"))
    except (OSError, ValueError):
        raise SystemExit("Operations preparation failed; inspect private paths") from None
    print("Dedicated operations paths prepared; existing credentials retained, values omitted")


if __name__ == "__main__":
    main()
