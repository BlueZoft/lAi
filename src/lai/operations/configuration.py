"""Check normalised Compose controls without starting Docker services."""

from collections.abc import Mapping


def validate_runtime(config: object) -> None:
    if not isinstance(config, Mapping):
        raise ValueError("unexpected_runtime_configuration")
    services = config.get("services")
    if not isinstance(services, Mapping) or set(services) != {"app", "db"}:
        raise ValueError("unexpected_runtime_services")
    for name, service in services.items():
        if not isinstance(service, Mapping):
            raise ValueError("unexpected_runtime_service")
        if (
            service.get("network_mode") != "none"
            or service.get("ports")
            or service.get("networks")
            or service.get("privileged")
            or not service.get("read_only")
            or service.get("pid") == "host"
            or service.get("logging", {}).get("driver") != "none"
            or not 0 < int(service.get("mem_limit", 0)) <= 2 * 1024**3
            or not 0 < int(service.get("pids_limit", 0)) <= 128
            or "no-new-privileges:true" not in service.get("security_opt", [])
            or service.get("pull_policy") != "never"
        ):
            raise ValueError("unsafe_runtime_controls")
        targets = {volume["target"] for volume in service.get("volumes", [])}
        allowed = (
            {"/run/lai-api", "/etc/resolv.conf"}
            if name == "app"
            else {"/var/lib/postgresql/data", "/var/run/postgresql"}
        )
        if targets != allowed:
            raise ValueError("unexpected_runtime_mount")
