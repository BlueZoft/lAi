"""GnuPG authenticated encrypted synthetic dumps. Keys/cleartext never enter argv."""

import subprocess
from pathlib import Path


def crypt(data: bytes, passphrase: Path, home: Path, *, decrypt: bool = False) -> bytes:
    if (
        passphrase.is_symlink()
        or passphrase.stat().st_mode & 0o077
        or passphrase.stat().st_size < 32
        or len(data) > 16 * 1024**2
    ):
        raise ValueError("unsafe_synthetic_backup_input")
    home.mkdir(mode=0o700, exist_ok=True)
    command = [
        "gpg",
        "--homedir",
        str(home),
        "--batch",
        "--no-tty",
        "--pinentry-mode",
        "loopback",
        "--passphrase-file",
        str(passphrase),
        "--no-symkey-cache",
    ]
    command.extend(
        ["--decrypt"]
        if decrypt
        else [
            "--symmetric",
            "--cipher-algo",
            "AES256",
            "--compress-algo",
            "none",
            "--s2k-digest-algo",
            "SHA512",
            "--s2k-mode",
            "3",
        ]
    )
    try:
        result = subprocess.run(command, input=data, capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError("backup_crypto_failed")
        return result.stdout
    finally:
        # GnuPG may spawn an agent even for symmetric loopback operation. Stop only this home.
        stopped = subprocess.run(
            ["gpgconf", "--homedir", str(home), "--kill", "gpg-agent"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
        if stopped.returncode:
            raise RuntimeError("backup_agent_cleanup_failed")
