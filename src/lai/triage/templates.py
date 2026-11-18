"""Versioned fixed copy. Draft Sinhala/English text cannot become public copy implicitly."""

from datetime import date
from importlib.resources import files
from typing import Literal, Self

from pydantic import Field, model_validator

from lai.corpus.models import Contract
from lai.triage.contracts import TemplateId, TriageDecision


class SafetyTemplate(Contract):
    id: TemplateId
    language: Literal["en", "si"]
    text: str = Field(min_length=1, max_length=1000)
    review_status: Literal["UNREVIEWED", "APPROVED"] = "UNREVIEWED"
    attorney_reviewed_on: date | None = None
    language_reviewed_on: date | None = None

    @model_validator(mode="after")
    def review_evidence(self) -> Self:
        if "{" in self.text or "}" in self.text:
            raise ValueError("safety_template_must_be_fixed")
        dates = (self.attorney_reviewed_on, self.language_reviewed_on)
        if (self.review_status == "APPROVED") != all(dates):
            raise ValueError("template_review_evidence_inconsistent")
        if self.review_status == "UNREVIEWED" and any(dates):
            raise ValueError("incomplete_template_review")
        return self


class SafetyTemplates(Contract):
    schema_version: Literal["1"] = "1"
    revision: str
    templates: tuple[SafetyTemplate, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def complete_unique_copy(self) -> Self:
        keys = {(item.id, item.language) for item in self.templates}
        required = {
            (key, language)
            for key in ("urgent", "refuse", "professional", "limitation", "abstain", "extractive")
            for language in ("en", "si")
        }
        if len(keys) != len(self.templates) or keys != required:
            raise ValueError("safety_template_set_incomplete_or_duplicate")
        return self


def load_templates() -> SafetyTemplates:
    return SafetyTemplates.model_validate_json(
        files("lai.triage").joinpath("data/templates.json").read_bytes()
    )


def approved_messages(
    decision: TriageDecision,
    language: Literal["en", "si"],
    as_of: date,
    register: SafetyTemplates | None = None,
) -> tuple[str, ...]:
    register = register or load_templates()
    selected = [
        next(item for item in register.templates if item.id == key and item.language == language)
        for key in decision.template_ids
    ]
    if any(
        item.review_status != "APPROVED"
        or item.attorney_reviewed_on is None
        or item.language_reviewed_on is None
        or item.attorney_reviewed_on > as_of
        or item.language_reviewed_on > as_of
        for item in selected
    ):
        return ()
    return tuple(item.text for item in selected)
