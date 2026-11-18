import json
from datetime import date
from pathlib import Path

import pytest
from conftest import RetrievalContext
from pydantic import ValidationError

from lai.retrieval.cli import main
from lai.retrieval.engine import Retriever
from lai.retrieval.evaluation import EvaluationDataset, evaluate
from lai.retrieval.models import RetrievalPolicy


def dataset() -> EvaluationDataset:
    return EvaluationDataset.model_validate_json(
        (Path(__file__).parent / "fixtures/retrieval-queries.json").read_bytes()
    )


def test_synthetic_cli_emits_only_aggregate_measurements(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--as-of", "2026-11-18", "demo"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["queries"] == 5
    assert report["backend_kind"] == "fake"
    assert report["dataset_kind"] == "synthetic"
    assert report["legal_validation"] == "UNVERIFIED"
    assert report["recall_at_15"] == 1.0
    assert "query" not in report and "candidates" not in report


def test_fake_metrics_cannot_be_labelled_legal(retrieval_context: RetrievalContext) -> None:
    context = retrieval_context
    engine = Retriever(
        context.catalog, context.index, context.backend, RetrievalPolicy(enabled=True)
    )
    data = dataset().model_copy(update={"kind": "legal"})
    with pytest.raises(ValueError, match="fake_evaluation_requires_synthetic_dataset"):
        evaluate(engine, data, date(2026, 11, 18))


def test_duplicate_evaluation_cases_are_rejected() -> None:
    data = dataset().model_dump(mode="json")
    data["cases"].append(data["cases"][0])
    with pytest.raises(ValidationError, match="duplicate_evaluation_case"):
        EvaluationDataset.model_validate_json(json.dumps(data))
