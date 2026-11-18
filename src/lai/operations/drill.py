"""Execute only a fresh synthetic Compose project, then remove its own containers/volume."""

import json
import os
import re
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from lai.corpus.models import digest
from lai.operations.backup import crypt
from lai.operations.prepare import prepare

ROOT = Path(__file__).resolve().parents[3]
DOCKER = ["docker", "--host=unix:///var/run/docker.sock"]


def run(command: list[str], data: bytes | None = None, timeout: int = 120) -> bytes:
    result = subprocess.run(command, input=data, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError("operations_command_failed")
    return result.stdout


def run_drill(temporary: Path) -> dict[str, object]:
    project = "lai-t7-test-" + uuid4().hex[:8]
    prepare(temporary)
    compose = DOCKER + ["compose", "-f", str(ROOT / "compose.runtime.yaml"), "-p", project]
    # This variable is a local path, never a credential or query. Do not persist it globally.
    env = os.environ.copy()
    env["LAI_OPERATIONS_DIR"] = str(temporary)

    def command(arguments: list[str], data: bytes | None = None) -> bytes:
        result = subprocess.run(
            compose + arguments,
            input=data,
            capture_output=True,
            env=env,
            timeout=180,
        )
        if result.returncode:
            raise RuntimeError("synthetic_compose_operation_failed")
        return result.stdout

    if command(["ps", "--all", "--quiet"]).strip():
        raise RuntimeError("synthetic_project_already_exists")
    try:
        command(["up", "--detach", "--wait", "--wait-timeout", "100"])
        app, db = (
            command(["ps", "--quiet", service]).decode().strip() for service in ("app", "db")
        )
        if not all(re.fullmatch(r"[0-9a-f]{64}", identifier) for identifier in (app, db)):
            raise RuntimeError("unexpected_container_identity")
        report: dict[str, object] = {
            "schema_version": "1",
            "kind": "synthetic",
            "public_launch": False,
        }
        for name, container in (("app", app), ("db", db)):
            config = json.loads(run(DOCKER + ["inspect", container]))[0]
            host = config["HostConfig"]
            if host["NetworkMode"] != "none" or host["LogConfig"]["Type"] != "none":
                raise RuntimeError("unsafe_runtime_configuration")
            if host.get("PortBindings") or config["NetworkSettings"].get("Ports"):
                raise RuntimeError("unexpected_port_publication")
            report[name + "_network_none"] = True
            report[name + "_docker_logs_disabled"] = True
            # Probe each actual service namespace with the already-built tiny image.
            response = run(
                DOCKER
                + [
                    "run",
                    "--rm",
                    "--network",
                    "container:" + container,
                    "--read-only",
                    "--cap-drop=ALL",
                    "--security-opt=no-new-privileges:true",
                    "--log-driver=none",
                    "--mount",
                    f"type=bind,src={ROOT / 'operations/resolv.conf'},"
                    "dst=/etc/resolv.conf,readonly",
                    "--entrypoint",
                    "python",
                    "lai-runtime:t7",
                    "-m",
                    "lai.operations.probe",
                    "network",
                ]
            )
            checks = json.loads(response)
            if not all(checks.values()):
                raise RuntimeError("runtime_egress_probe_failed")
            report[name + "_egress_checks"] = checks
        report["http_checks"] = json.loads(
            run(
                DOCKER
                + [
                    "exec",
                    app,
                    "python",
                    "-m",
                    "lai.operations.probe",
                    "http",
                ]
            )
        )
        state = json.loads(run(DOCKER + ["inspect", app]))[0]["HostConfig"]
        report["app_read_only_root"] = state["ReadonlyRootfs"] is True
        report["app_memory_limit_mib"] = state["Memory"] // 1024**2
        if not report["app_read_only_root"]:
            raise RuntimeError("writable_application_root")

        def sql(statement: str, database: str = "lai_runtime") -> bytes:
            return command(
                [
                    "exec",
                    "-T",
                    "db",
                    "psql",
                    "-X",
                    "-q",
                    "-t",
                    "-A",
                    "-v",
                    "ON_ERROR_STOP=1",
                    "-U",
                    "lai_ops",
                    "-d",
                    database,
                ],
                statement.encode(),
            )

        sql("""CREATE EXTENSION vector;
            CREATE SCHEMA synthetic_drill;
            CREATE TABLE synthetic_drill.entries(
                id integer PRIMARY KEY, label text, embedding vector(3));
            INSERT INTO synthetic_drill.entries VALUES
                (1,'SYNTHETIC catalogue','[1,0,0]'),
                (2,'SYNTHETIC counter','[0,1,0]'),
                (3,'SYNTHETIC document','[0,0,1]');""")
        select = "SELECT id,label,embedding::text FROM synthetic_drill.entries ORDER BY id;"
        before = sql(select)
        dump = command(
            [
                "exec",
                "-T",
                "db",
                "pg_dump",
                "-U",
                "lai_ops",
                "--format=custom",
                "--no-owner",
                "--no-privileges",
                "--dbname=lai_runtime",
            ]
        )
        if len(dump) > 16 * 1024**2 or b"SYNTHETIC_T7_PRIVATE_CANARY" in dump:
            raise RuntimeError("unexpected_dump_content")
        encrypted = crypt(dump, temporary / "backup.passphrase", temporary / "gpg")
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        backup = temporary / "retained/backups" / (stamp + ".gpg")
        fd = os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(encrypted)
        tampered = bytes([encrypted[0] ^ 0xFF]) + encrypted[1:]
        try:
            crypt(tampered, temporary / "backup.passphrase", temporary / "gpg", decrypt=True)
        except RuntimeError:
            report["corrupt_backup_rejected"] = True
        else:
            raise RuntimeError("corrupt_backup_accepted")
        recovered = crypt(
            backup.read_bytes(), temporary / "backup.passphrase", temporary / "gpg", decrypt=True
        )
        if digest(recovered) != digest(dump):
            raise RuntimeError("backup_roundtrip_mismatch")
        sql("CREATE DATABASE lai_restore;")
        command(
            [
                "exec",
                "-T",
                "db",
                "pg_restore",
                "-U",
                "lai_ops",
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "--dbname=lai_restore",
            ],
            recovered,
        )
        after = sql(select, "lai_restore")
        if before != after:
            raise RuntimeError("restored_source_rows_changed")
        report.update(
            {
                "restored_rows": 3,
                "restored_rows_sha256": digest(after),
                "encrypted_backup_sha256": digest(encrypted),
                "encrypted_backup_bytes": len(encrypted),
                "backup_plaintext_roundtrip": True,
                "request_canary_absent_from_dump": True,
                "gateway_host_controls": "UNVERIFIED",
                "laptop_hardware_fit": "UNVERIFIED",
                "legal_compliance": "UNVERIFIED",
            }
        )
        return report
    finally:
        command(["down", "--volumes", "--remove-orphans"])


def main() -> None:
    persistent = ROOT / ".local/operations"
    try:
        prepare(persistent)
        with tempfile.TemporaryDirectory(prefix="t7-check-", dir=ROOT / ".local") as directory:
            report = run_drill(Path(directory))
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        path = persistent / "retained/reports" / (stamp + ".json")
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(report, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except Exception:
        raise SystemExit(
            "Synthetic operations drill failed; inspect the isolated project"
        ) from None
    print(json.dumps(report, sort_keys=True))
    print("Owned synthetic project and scratch keys/dumps removed; aggregate report retained")


if __name__ == "__main__":
    main()
