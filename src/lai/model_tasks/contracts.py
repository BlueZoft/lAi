"""Strict, source-anchored proposals; no model output is a legal answer."""

from typing import Annotated, Literal, Self, cast

from pydantic import Field, TypeAdapter, model_validator

from lai.corpus.models import Contract, Sha256, digest
from lai.triage.contracts import Domain, TriageDecision, TriageRequest

Task = Literal["language", "transliterate", "intent", "entities", "rewrite", "extractive_summary"]
Script = Literal["latin", "sinhala", "tamil", "unsupported"]


class SourceExcerpt(Contract):
    text: str = Field(min_length=1, max_length=4096)
    sha256: Sha256

    @model_validator(mode="after")
    def bound_bytes(self) -> Self:
        if digest(self.text.encode("utf-8")) != self.sha256:
            raise ValueError("excerpt_hash_mismatch")
        return self


class TaskRequest(Contract):
    schema_version: Literal["1"] = "1"
    task: Task
    scenario: TriageRequest
    source: SourceExcerpt | None = None

    @model_validator(mode="after")
    def correct_context(self) -> Self:
        if (self.task == "extractive_summary") != (self.source is not None):
            raise ValueError("source_only_for_extracts")
        if self.task == "transliterate" and self.scenario.language != "si-Latn":
            raise ValueError("transliteration_requires_explicit_singlish")
        return self


class Span(Contract):
    """Python Unicode code-point offsets, end exclusive; never byte offsets."""

    start: int = Field(ge=0, le=4095)
    end: int = Field(gt=0, le=4096)
    text: str = Field(min_length=1, max_length=1024)

    @model_validator(mode="after")
    def valid_length(self) -> Self:
        if self.end - self.start != len(self.text):
            raise ValueError("span_length_mismatch")
        return self


class LanguageOutput(Contract):
    task: Literal["language"] = "language"
    scripts: tuple[Script, ...] = Field(max_length=4)
    language: Literal["en", "si", "ta", "si-Latn", "mixed", "und"]


class TransliterationOutput(Contract):
    task: Literal["transliterate"] = "transliterate"
    text: str = Field(min_length=1, max_length=1024)


class IntentOutput(Contract):
    task: Literal["intent"] = "intent"
    domain: Domain


class Entity(Contract):
    kind: Literal["date", "amount", "district", "employment_status"]
    span: Span


class EntitiesOutput(Contract):
    task: Literal["entities"] = "entities"
    entities: tuple[Entity, ...] = Field(max_length=8)


class RewriteOutput(Contract):
    task: Literal["rewrite"] = "rewrite"
    spans: tuple[Span, ...] = Field(min_length=1, max_length=8)


class ExtractOutput(Contract):
    task: Literal["extractive_summary"] = "extractive_summary"
    source_sha256: Sha256
    spans: tuple[Span, ...] = Field(min_length=1, max_length=3)


Completion = Annotated[
    LanguageOutput
    | TransliterationOutput
    | IntentOutput
    | EntitiesOutput
    | RewriteOutput
    | ExtractOutput,
    Field(discriminator="task"),
]
# Pydantic accepts annotated unions; its constructor annotation expects a class.
COMPLETION: TypeAdapter[Completion] = TypeAdapter(cast(type[Completion], Completion))
OUTPUT_TYPES: dict[Task, type[Contract]] = {
    "language": LanguageOutput,
    "transliterate": TransliterationOutput,
    "intent": IntentOutput,
    "entities": EntitiesOutput,
    "rewrite": RewriteOutput,
    "extractive_summary": ExtractOutput,
}


class TaskOutcome(Contract):
    schema_version: Literal["1"] = "1"
    status: Literal["validated", "fallback", "blocked"]
    reason: Literal[
        "validated_proposal",
        "safety_route",
        "invalid_request",
        "unavailable",
        "invalid_output",
        "busy",
    ]
    decision: TriageDecision
    output: Completion | None = None
    deterministic_output: (
        Annotated[
            LanguageOutput | IntentOutput | EntitiesOutput | RewriteOutput,
            Field(discriminator="task"),
        ]
        | None
    ) = None
    fallback: Literal[
        "none",
        "scripts_only",
        "no_transliteration",
        "unknown_intent",
        "omit_entities",
        "original_query",
        "no_summary",
    ] = "none"
    product_enabled: Literal[False] = False
    language_quality: Literal["UNVERIFIED"] = "UNVERIFIED"

    @model_validator(mode="after")
    def no_output_on_failure(self) -> Self:
        if (self.status == "validated") != (self.output is not None):
            raise ValueError("only_validated_proposals_have_output")
        if self.status == "validated" and (
            self.reason != "validated_proposal"
            or self.fallback != "none"
            or self.deterministic_output is not None
        ):
            raise ValueError("invalid_success")
        if self.status == "blocked" and (
            self.fallback != "none"
            or self.deterministic_output is not None
            or self.reason not in {"safety_route", "invalid_request"}
        ):
            raise ValueError("blocked_has_no_fallback")
        if self.status == "fallback":
            if self.reason not in {"unavailable", "invalid_output", "busy"}:
                raise ValueError("invalid_failure_reason")
            value = self.deterministic_output
            expected = {
                "scripts_only": "language",
                "unknown_intent": "intent",
                "omit_entities": "entities",
                "original_query": "rewrite",
            }
            if (value.task if value is not None else None) != expected.get(self.fallback):
                raise ValueError("wrong_deterministic_fallback")
            if self.fallback == "none":
                raise ValueError("fallback_action_required")
            if isinstance(value, IntentOutput) and value.domain != "unknown":
                raise ValueError("fallback_intent_must_be_unknown")
            if isinstance(value, EntitiesOutput) and value.entities:
                raise ValueError("fallback_has_no_entities")
            if isinstance(value, RewriteOutput) and (
                len(value.spans) != 1 or value.spans[0].start != 0
            ):
                raise ValueError("fallback_keeps_whole_original_query")
        if (self.output is not None or self.deterministic_output is not None) and (
            self.decision.action
            in {
                "immediate_escalation",
                "professional_referral",
                "refuse",
            }
        ):
            raise ValueError("safety_route_has_no_model_output")
        return self
