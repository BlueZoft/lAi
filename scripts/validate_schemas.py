"""Validate versioned release evidence against the committed contract."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from lai.safety import LaunchGate

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    schema = json.loads((ROOT / "schemas/launch-gate.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    data = json.loads((ROOT / "config/launch-gate.json").read_text())
    Draft202012Validator(schema).validate(data)
    gate = LaunchGate.model_validate(data)
    if gate.allows_public_launch():
        raise SystemExit("Private prototype configuration must keep the public launch gate closed")
    print("Launch-gate schema valid; public launch blocked")


if __name__ == "__main__":
    main()
