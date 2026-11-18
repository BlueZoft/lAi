import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError
from pydantic import BaseModel

from lai.corpus.graph import VersionGraph
from lai.corpus.models import IngestionRecord, SourceManifest
from lai.retrieval.evaluation import EvaluationDataset
from lai.retrieval.models import RetrievalPolicy, RetrievalResult
from lai.safety import LaunchGate
from lai.triage.contracts import NavigationOutcome, SafetyPolicy, TriageDecision, TriageRequest
from lai.triage.referrals import ReferralRegister
from lai.triage.templates import SafetyTemplates

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


@pytest.mark.parametrize(
    ("name", "contract"),
    [
        ("source-manifest", SourceManifest),
        ("ingestion-record", IngestionRecord),
        ("version-graph", VersionGraph),
        ("retrieval-policy", RetrievalPolicy),
        ("retrieval-result", RetrievalResult),
        ("evaluation-dataset", EvaluationDataset),
        ("triage-request", TriageRequest),
        ("triage-decision", TriageDecision),
        ("safety-policy", SafetyPolicy),
        ("navigation-outcome", NavigationOutcome),
        ("referral-register", ReferralRegister),
        ("safety-templates", SafetyTemplates),
    ],
)
def test_corpus_schemas_match_typed_contracts(
    name: str,
    contract: type[BaseModel],
) -> None:
    schema = json.loads((ROOT / f"schemas/{name}.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    assert schema == contract.model_json_schema()
