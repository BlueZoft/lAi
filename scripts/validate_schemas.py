"""Validate versioned release evidence against the committed contract."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from lai.corpus.graph import VersionGraph, document_nodes
from lai.corpus.ingest import ingest_document
from lai.corpus.models import IngestionRecord, SourceManifest
from lai.retrieval.evaluation import EvaluationDataset
from lai.retrieval.models import RetrievalPolicy, RetrievalResult
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
    manifest = SourceManifest.model_validate_json(
        (ROOT / "tests/fixtures/synthetic-act.manifest.json").read_bytes()
    )
    raw = (ROOT / "tests/fixtures/synthetic-act.txt").read_bytes()
    record = ingest_document(manifest, raw, raw)
    graph = VersionGraph(nodes=document_nodes(record))
    examples = (
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
        print(f"{name} schema and synthetic example valid")


if __name__ == "__main__":
    main()
