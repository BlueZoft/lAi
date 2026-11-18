"""Aggregate private acceptance checks. Synthetic success never permits launch."""

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Literal, Self
from zoneinfo import ZoneInfo

from pydantic import Field, model_validator

from lai.corpus.models import Contract, Identifier, Sha256, digest
from lai.operations.retention import PrivacyPolicy
from lai.retrieval.cli import run_demo
from lai.retrieval.evaluation import EvaluationDataset
from lai.safety import LaunchGate
from lai.triage.contracts import Action, SafetyPolicy, TriageRequest
from lai.triage.pipeline import SafetyNavigator


class GoldenSet(Contract):
    schema_version: Literal["1"] = "1"
    dataset: EvaluationDataset
    dataset_sha256: Sha256
    scope: tuple[Identifier, ...] = Field(min_length=1)
    attorney_reviewed_on: date
    language_reviewed_on: date
    review_evidence_ref: Identifier
    split: Literal["calibration", "held_out"]

    @model_validator(mode="after")
    def bound_review(self) -> Self:
        if self.dataset.kind != "legal":
            raise ValueError("golden_set_requires_legal_labels")
        if digest(self.dataset.model_dump_json().encode()) != self.dataset_sha256:
            raise ValueError("reviewed_dataset_changed")
        today = datetime.now(ZoneInfo("Asia/Colombo")).date()
        if self.attorney_reviewed_on > today or self.language_reviewed_on > today:
            raise ValueError("future_review")
        return self


class RedCase(Contract):
    id: Identifier
    payload: dict[str, object]
    expected: Action


class RedSuite(Contract):
    kind: Literal["synthetic"] = "synthetic"
    cases: tuple[RedCase, ...] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_ids(self) -> Self:
        if len({case.id for case in self.cases}) != len(self.cases):
            raise ValueError("duplicate_red_case")
        if any(case.expected == "navigate" for case in self.cases):
            raise ValueError("red_suite_contains_only_blocked_requests")
        return self


def red_team(suite: RedSuite, as_of: date) -> dict[str, object]:
    from lai.retrieval.models import RetrievalResult

    class Spy:
        calls = 0

        def run(self, request: TriageRequest, as_of: date) -> RetrievalResult:
            self.calls += 1
            return RetrievalResult(status="abstained", reasons=("synthetic_spy",))

    passed = 0
    downstream_calls = 0
    for case in suite.cases:
        spy = Spy()
        outcome = SafetyNavigator(spy, SafetyPolicy(research_navigation_enabled=True)).handle(
            case.payload, as_of
        )
        passed += outcome.decision.action == case.expected and spy.calls == 0
        downstream_calls += spy.calls
    return {
        "kind": "synthetic",
        "cases": len(suite.cases),
        "passed": passed,
        "downstream_calls": downstream_calls,
        "language_validation": "UNVERIFIED",
    }


def release_status(gate: LaunchGate, *, legal_evidence_verified: bool = False) -> dict[str, object]:
    gate = LaunchGate.model_validate_json(gate.model_dump_json())
    missing = [name for name, value in gate.model_dump().items() if not value]
    # Manual booleans are assertions, not independently checked evidence.
    return {
        "decision": "GO" if gate.allows_public_launch() and legal_evidence_verified else "NO-GO",
        "configuration_allows_launch": gate.allows_public_launch(),
        "independent_legal_evidence_verified": legal_evidence_verified,
        "false_configuration_flags": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.repository
    suite = RedSuite.model_validate_json((root / "tests/fixtures/red-team.json").read_bytes())
    gate = LaunchGate.model_validate_json((root / "config/launch-gate.json").read_bytes())
    # The CLI has no flag that can manufacture independent legal evidence.
    report = {
        "schema_version": "1",
        "kind": "synthetic",
        "red_team": red_team(suite, date(2026, 11, 19)),
        "retrieval": run_demo(argparse.Namespace(postgres=False, as_of=date(2026, 11, 19))),
        "release": release_status(gate),
        "legal_golden_set": "UNVERIFIED",
        "legal_threshold_calibration": "UNVERIFIED",
        "privacy_policy": PrivacyPolicy().model_dump(mode="json"),
    }
    print(json.dumps(report, sort_keys=True))
    red = report["red_team"]
    if isinstance(red, dict) and red["cases"] != red["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
