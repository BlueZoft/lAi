"""The only product-facing entry contract: decide before invoking any downstream work."""

from datetime import date
from typing import Protocol

from lai.retrieval.engine import Retriever
from lai.retrieval.models import RetrievalResult
from lai.triage.contracts import NavigationOutcome, SafetyPolicy, TriageDecision, TriageRequest
from lai.triage.rules import decide


class NavigationPath(Protocol):
    """Entire downstream analysis/model/retrieval path, inaccessible on a blocked route."""

    def run(self, request: TriageRequest, as_of: date) -> RetrievalResult: ...


class RetrievalNavigation:
    """T3 adapter; no language model or legal-analysis stage is introduced in T4."""

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def run(self, request: TriageRequest, as_of: date) -> RetrievalResult:
        return self.retriever.retrieve(request.text, as_of, request.language)


class SafetyNavigator:
    def __init__(self, downstream: NavigationPath, policy: SafetyPolicy | None = None):
        self.downstream = downstream
        self.policy = policy or SafetyPolicy()

    def handle(self, payload: object, as_of: date) -> NavigationOutcome:
        decision = decide(payload, self.policy)
        if decision.action != "navigate":
            return NavigationOutcome(decision=decision)
        request = TriageRequest.model_validate(payload)
        try:
            result = self.downstream.run(request, as_of)
            result = RetrievalResult.model_validate_json(result.model_dump_json())
        except Exception:
            return NavigationOutcome(
                decision=TriageDecision(
                    action="abstain", reasons=("downstream_unavailable",), template_ids=("abstain",)
                )
            )
        if result.status == "abstained":
            return NavigationOutcome(
                decision=TriageDecision(
                    action="abstain",
                    reasons=("insufficient_source_evidence",),
                    template_ids=("abstain",),
                )
            )
        return NavigationOutcome(decision=decision, retrieval=result)
