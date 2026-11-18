from copy import deepcopy

import pytest

from lai.operations.configuration import validate_runtime


def configuration() -> dict[str, object]:
    shared: dict[str, object] = {
        "network_mode": "none",
        "read_only": True,
        "logging": {"driver": "none"},
        "mem_limit": 512 * 1024**2,
        "pids_limit": 64,
        "pull_policy": "never",
        "security_opt": ["no-new-privileges:true"],
    }
    app = {
        **deepcopy(shared),
        "volumes": [
            {"target": "/run/lai-api"},
            {"target": "/etc/resolv.conf"},
        ],
    }
    db = {
        **deepcopy(shared),
        "volumes": [
            {"target": "/var/lib/postgresql/data"},
            {"target": "/var/run/postgresql"},
        ],
    }
    return {"services": {"app": app, "db": db}}


def test_isolated_configuration_is_accepted() -> None:
    validate_runtime(configuration())


@pytest.mark.safety
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("network_mode", "host"),
        ("ports", ["8000:8000"]),
        ("read_only", False),
        ("logging", {"driver": "json-file"}),
        ("privileged", True),
        ("pid", "host"),
        ("mem_limit", 0),
        ("pids_limit", 10000),
        ("security_opt", []),
        ("pull_policy", "always"),
        ("volumes", [{"target": "/var/run/docker.sock"}]),
    ],
)
def test_weakened_runtime_controls_are_rejected(field: str, value: object) -> None:
    config = configuration()
    services = config["services"]
    assert isinstance(services, dict)
    services["app"][field] = value
    with pytest.raises(ValueError):
        validate_runtime(config)
