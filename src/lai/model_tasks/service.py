"""Private research facade. No integration with answer assembly or retrieval."""

from collections.abc import Mapping
from threading import Lock
from typing import Protocol

from lai.model_tasks.contracts import (
    EntitiesOutput,
    IntentOutput,
    RewriteOutput,
    Span,
    TaskOutcome,
    TaskRequest,
)
from lai.model_tasks.prompts import build_prompt
from lai.model_tasks.validation import script_result, validate_output
from lai.retrieval.query import plan_query
from lai.triage.rules import decide

# Reject rather than queue. Shared across instances in this process, including CPU mode.
MODEL_SLOT = Lock()
FALLBACKS = {
    "language": "scripts_only",
    "transliterate": "no_transliteration",
    "intent": "unknown_intent",
    "entities": "omit_entities",
    "rewrite": "original_query",
    "extractive_summary": "no_summary",
}


class CompletionBackend(Protocol):
    def complete(self, prompt: str, schema: dict[str, object]) -> bytes: ...


class BoundedModel:
    def __init__(self, backend: CompletionBackend | None = None):
        self.backend = backend

    def run(self, payload: object) -> TaskOutcome:
        raw = payload if isinstance(payload, Mapping) else {}
        scenario = raw.get("scenario")
        decision = decide(scenario)
        # Always inspect bounded raw urgency first, even if task/source/envelope is malformed.
        if decision.action in {"immediate_escalation", "professional_referral", "refuse"}:
            return TaskOutcome(status="blocked", reason="safety_route", decision=decision)
        try:
            request = TaskRequest.model_validate(payload)
            # Do not trust unchecked model_copy/model_construct instances at this boundary.
            request = TaskRequest.model_validate_json(request.model_dump_json())
            if any(reason in {"invalid_request", "invalid_text"} for reason in decision.reasons):
                raise ValueError("invalid_scenario")
            # Singlish is measured here only; it remains unsupported in product triage.
            hint = None if request.scenario.language == "si-Latn" else request.scenario.language
            plan_query(request.scenario.text, hint)
            if request.task == "transliterate" and script_result(request).scripts != ("latin",):
                raise ValueError("not_singlish_script")
        except (ValueError, TypeError, UnicodeError):
            return TaskOutcome(status="blocked", reason="invalid_request", decision=decision)

        def failed(reason: str) -> TaskOutcome:
            deterministic = None
            if request.task == "language":
                deterministic = script_result(request).model_dump(mode="python")
            elif request.task == "intent":
                deterministic = IntentOutput(domain="unknown").model_dump(mode="python")
            elif request.task == "entities":
                deterministic = EntitiesOutput(entities=()).model_dump(mode="python")
            elif request.task == "rewrite":
                text = request.scenario.text
                deterministic = RewriteOutput(
                    spans=(Span(start=0, end=len(text), text=text),)
                ).model_dump(mode="python")
            return TaskOutcome.model_validate(
                {
                    "status": "fallback",
                    "reason": reason,
                    "decision": decision,
                    "fallback": FALLBACKS[request.task],
                    "deterministic_output": deterministic,
                }
            )

        if self.backend is None:
            return failed("unavailable")
        if not MODEL_SLOT.acquire(blocking=False):
            return failed("busy")
        try:
            prompt, schema = build_prompt(request)
            try:
                response = self.backend.complete(prompt, schema)
            except Exception:
                return failed("unavailable")
            try:
                output = validate_output(response, request, decision)
            except (ValueError, TypeError, RecursionError, UnicodeError):
                return failed("invalid_output")
            return TaskOutcome(
                status="validated", reason="validated_proposal", decision=decision, output=output
            )
        finally:
            MODEL_SLOT.release()
