import json
from pathlib import Path

import pytest

from lai.model_tasks.local import InferenceBudget
from lai.model_tasks.measure import MeasurementDataset, ReplayBackend, measure, write_report

FIXTURE = Path(__file__).parent / "fixtures/model-tasks.json"


def test_committed_budget_matches_the_measured_adapter_defaults() -> None:
    path = Path(__file__).parents[1] / "config/model-budget.json"
    assert InferenceBudget.model_validate_json(path.read_bytes()) == InferenceBudget()


def test_replay_is_explicitly_synthetic_and_not_a_quality_measurement(tmp_path: Path) -> None:
    dataset = MeasurementDataset.model_validate_json(FIXTURE.read_bytes())
    report = measure(dataset, ReplayBackend())
    assert report["backend_kind"] == "fake" and report["resource_fit"] == "UNVERIFIED"
    assert report["sinhala_capability"] == "UNVERIFIED" and not report["product_enabled"]
    assert report["sampled_peak_process_ram_mib"] is None
    text = json.dumps(report)
    for case in dataset.cases:
        assert case.request.scenario.text not in text
    output = tmp_path / ".local/report.json"
    write_report(output, report)
    assert output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        write_report(output, report)
    with pytest.raises(ValueError):
        write_report(tmp_path / "tracked.json", report)


def test_fake_labels_validate_every_task_and_block_urgent_examples() -> None:
    dataset = MeasurementDataset.model_validate_json(FIXTURE.read_bytes())
    report = measure(dataset, ReplayBackend(), repetitions=2)
    groups = report["groups"]
    assert isinstance(groups, list)
    assert {group["task"] for group in groups} == {
        "language",
        "transliterate",
        "intent",
        "entities",
        "rewrite",
        "extractive_summary",
    }
    assert all(group["exact_match"] == group["cases"] for group in groups)
    assert sum(group["blocked"] for group in groups) == 12


def test_review_cannot_be_claimed_without_evidence() -> None:
    dataset = json.loads(FIXTURE.read_bytes())
    dataset["review_status"] = "LANGUAGE_REVIEWED"
    with pytest.raises(ValueError):
        MeasurementDataset.model_validate_json(json.dumps(dataset))
