"""Validate versioned release evidence against the committed contract."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from lai.answers.contracts import AnswerDocument, AnswerRequest, GlossLibrary
from lai.answers.service import load_glosses
from lai.corpus.graph import VersionGraph, document_nodes
from lai.corpus.ingest import ingest_document
from lai.corpus.models import IngestionRecord, SourceManifest
from lai.model_tasks.contracts import TaskOutcome, TaskRequest
from lai.model_tasks.local import InferenceBudget, ModelManifest
from lai.model_tasks.measure import MeasurementDataset
from lai.model_tasks.service import BoundedModel
from lai.operations.retention import PrivacyPolicy
from lai.retrieval.evaluation import EvaluationDataset
from lai.retrieval.models import RetrievalPolicy, RetrievalResult
from lai.safety import LaunchGate
from lai.triage.contracts import NavigationOutcome, SafetyPolicy, TriageDecision, TriageRequest
from lai.triage.referrals import ReferralRegister, load_referrals
from lai.triage.rules import decide
from lai.triage.templates import SafetyTemplates, load_templates

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
    manifest = SourceManifest.model_validate_json(
        (ROOT / "tests/fixtures/synthetic-act.manifest.json").read_bytes()
    )
    raw = (ROOT / "tests/fixtures/synthetic-act.txt").read_bytes()
    record = ingest_document(manifest, raw, raw)
    graph = VersionGraph(nodes=document_nodes(record))
    examples = (
        (
            "privacy-policy",
            PrivacyPolicy,
            PrivacyPolicy.model_validate_json(
                (ROOT / "config/privacy-policy.json").read_bytes()
            ).model_dump(mode="json"),
        ),
        ("model-task-request", TaskRequest, {"task": "intent", "scenario": {"text": "SYNTHETIC"}}),
        ("model-task-outcome", TaskOutcome, BoundedModel().run(None).model_dump(mode="json")),
        ("model-inference-budget", InferenceBudget, InferenceBudget().model_dump(mode="json")),
        (
            "local-model-manifest",
            ModelManifest,
            {
                "model_id": "SYNTHETIC",
                "revision": "synthetic-v1",
                "runner_revision": "0" * 40,
                "model_sha256": "0" * 64,
                "executable_sha256": "0" * 64,
                "parameters_billions": 4.0,
                "licence_evidence_ref": "synthetic-test-only",
            },
        ),
        (
            "model-measurement-dataset",
            MeasurementDataset,
            MeasurementDataset.model_validate_json(
                (ROOT / "tests/fixtures/model-tasks.json").read_bytes()
            ).model_dump(mode="json"),
        ),
        ("answer-request", AnswerRequest, {"scenario": {"text": "SYNTHETIC documents"}}),
        ("gloss-library", GlossLibrary, load_glosses().model_dump(mode="json")),
        (
            "answer-document",
            AnswerDocument,
            AnswerDocument(
                status="review_required",
                as_of=record.manifest.source.fetched_at.date(),
                decision=decide({"text": "SYNTHETIC documents"}),
            ).model_dump(mode="json"),
        ),
        ("triage-request", TriageRequest, {"text": "SYNTHETIC documents"}),
        (
            "triage-decision",
            TriageDecision,
            decide({"text": "SYNTHETIC documents"}).model_dump(mode="json"),
        ),
        ("safety-policy", SafetyPolicy, SafetyPolicy().model_dump(mode="json")),
        (
            "navigation-outcome",
            NavigationOutcome,
            NavigationOutcome(decision=decide({"text": "SYNTHETIC documents"})).model_dump(
                mode="json"
            ),
        ),
        ("referral-register", ReferralRegister, load_referrals().model_dump(mode="json")),
        ("safety-templates", SafetyTemplates, load_templates().model_dump(mode="json")),
        ("source-manifest", SourceManifest, manifest.model_dump(mode="json")),
        ("ingestion-record", IngestionRecord, record.model_dump(mode="json")),
        ("version-graph", VersionGraph, graph.model_dump(mode="json")),
        ("retrieval-policy", RetrievalPolicy, RetrievalPolicy().model_dump(mode="json")),
        (
            "retrieval-result",
            RetrievalResult,
            RetrievalResult(status="abstained", reasons=("retrieval_disabled",)).model_dump(
                mode="json"
            ),
        ),
        (
            "evaluation-dataset",
            EvaluationDataset,
            EvaluationDataset.model_validate_json(
                (ROOT / "tests/fixtures/retrieval-queries.json").read_bytes()
            ).model_dump(mode="json"),
        ),
    )
    for name, contract, example in examples:
        schema = json.loads((ROOT / f"schemas/{name}.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        if schema != contract.model_json_schema():
            raise SystemExit(f"Committed schema differs from typed contract: {name}")
        Draft202012Validator(schema).validate(example)
        print(f"{name} schema and example valid")


if __name__ == "__main__":
    main()
