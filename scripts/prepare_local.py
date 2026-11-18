"""Create an ignored local secret without printing or replacing existing contents."""

import os
from pathlib import Path
from secrets import token_urlsafe

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    local = ROOT / ".local"
    if local.is_symlink():
        raise SystemExit("Local private configuration directory must not be a symlink")
    local.mkdir(mode=0o700, exist_ok=True)
    local.chmod(0o700)
    (local / "postgres-socket").mkdir(mode=0o700, exist_ok=True)
    password = local / "postgres.password"
    try:
        descriptor = os.open(password, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        if password.is_symlink() or not password.is_file():
            raise SystemExit("Existing local password path must be a regular file") from None
        if password.stat().st_mode & 0o077:
            raise SystemExit("Restrict .local/postgres.password permissions to 0600") from None
        if password.stat().st_size == 0:
            raise SystemExit("Existing local password file is empty") from None
        print("Local database configuration retained")
        return
    with os.fdopen(descriptor, "w") as stream:
        stream.write(token_urlsafe(32) + "\n")
    print("Local database configuration created (secret omitted)")


if __name__ == "__main__":
    main()
