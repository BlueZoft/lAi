import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from lai.safety import LaunchGate

ROOT = Path(__file__).resolve().parents[1]


def test_committed_schema_matches_typed_contract() -> None:
    schema = json.loads((ROOT / "schemas/launch-gate.schema.json").read_text())
    assert schema == LaunchGate.model_json_schema()


def test_versioned_evidence_validates_and_blocks_launch() -> None:
    schema = json.loads((ROOT / "schemas/launch-gate.schema.json").read_text())
    data = json.loads((ROOT / "config/launch-gate.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(data)
    assert not LaunchGate.model_validate(data).allows_public_launch()


@pytest.mark.parametrize("invalid", [{"dpia_complete": "yes"}, {"unknown": True}])
def test_schema_rejects_malformed_evidence(invalid: dict[str, object]) -> None:
    schema = json.loads((ROOT / "schemas/launch-gate.schema.json").read_text())
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(invalid)
