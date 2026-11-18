"""Invented labels only: these approval fixtures are not actual attorney reviews."""

import json
from datetime import date
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from lai.corpus.models import digest
from lai.evaluation import GoldenSet, RedSuite, red_team, release_status
from lai.retrieval.evaluation import EvaluationDataset
from lai.safety import LaunchGate

ROOT = Path(__file__).parents[1]


@pytest.mark.safety
def test_red_team_routes_and_downstream_short_circuits() -> None:
    suite = RedSuite.model_validate_json((ROOT / "tests/fixtures/red-team.json").read_bytes())
    result = red_team(suite, date(2026, 11, 19))
    assert result["passed"] == result["cases"] == 12
    assert result["downstream_calls"] == 0


@pytest.mark.safety
def test_even_asserted_release_flags_are_not_independent_evidence() -> None:
    flags = dict.fromkeys(LaunchGate.model_fields, True)
    gate = LaunchGate.model_validate(flags)
    assert gate.allows_public_launch()
    assert release_status(gate)["decision"] == "NO-GO"
    assert release_status(LaunchGate())["decision"] == "NO-GO"


def reviewed_fixture() -> dict[str, object]:
    data = json.loads((ROOT / "tests/fixtures/retrieval-queries.json").read_bytes())
    data["kind"] = "legal"  # Synthetic unit-test assertion, not a real legal golden set.
    dataset = EvaluationDataset.model_validate_json(json.dumps(data))
    return {
        "dataset": data,
        "dataset_sha256": digest(dataset.model_dump_json().encode()),
        "scope": ["SYNTHETIC-test"],
        "attorney_reviewed_on": "2020-01-01",
        "language_reviewed_on": "2020-01-01",
        "review_evidence_ref": "SYNTHETIC-only",
        "split": "held_out",
    }


def test_golden_review_is_bound_to_exact_dataset_and_split() -> None:
    payload = reviewed_fixture()
    golden = GoldenSet.model_validate_json(json.dumps(payload))
    assert golden.split == "held_out"
    payload["dataset_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="reviewed_dataset_changed"):
        GoldenSet.model_validate_json(json.dumps(payload))


def test_missing_or_future_review_cannot_be_approved() -> None:
    payload = reviewed_fixture()
    payload["attorney_reviewed_on"] = "2099-01-01"
    with pytest.raises(ValueError, match="future_review"):
        GoldenSet.model_validate_json(json.dumps(payload))
    del payload["attorney_reviewed_on"]
    with pytest.raises(ValueError):
        GoldenSet.model_validate_json(json.dumps(payload))


def test_golden_schema_matches_and_synthetic_labels_cannot_count_as_legal() -> None:
    schema = json.loads((ROOT / "schemas/legal-golden-set.schema.json").read_bytes())
    assert schema == GoldenSet.model_json_schema()
    Draft202012Validator.check_schema(schema)
    payload = reviewed_fixture()
    data = payload["dataset"]
    assert isinstance(data, dict)
    data["kind"] = "synthetic"
    with pytest.raises(ValueError, match="requires_legal"):
        GoldenSet.model_validate_json(json.dumps(payload))
