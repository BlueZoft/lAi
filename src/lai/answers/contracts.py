from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from lai.corpus.models import Contract, Identifier, Sha256, digest
from lai.retrieval.models import Candidate, Citation
from lai.triage.contracts import TriageDecision, TriageRequest
from lai.triage.referrals import Referral

DisplayLanguage = Literal["en", "si"]


class AnswerRequest(Contract):
    scenario: TriageRequest
    display_language: DisplayLanguage = "si"
    region: str | None = Field(default=None, min_length=1, max_length=100)


class Gloss(Contract):
    id: Identifier
    chunk_id: Sha256
    source_record_id: Sha256
    source_revision: str = Field(min_length=1, max_length=200)
    source_language: Literal["en", "si", "ta"]
    section_sha256: Sha256
    language: DisplayLanguage
    text: str = Field(min_length=1, max_length=2000)
    scope: Literal["procedural_explanation"] = "procedural_explanation"
    review_status: Literal["UNREVIEWED", "APPROVED"] = "UNREVIEWED"
    attorney_reviewed_on: date | None = None
    language_reviewed_on: date | None = None
    review_evidence_ref: Identifier | None = None
    reviewed_text_sha256: Sha256 | None = None

    @model_validator(mode="after")
    def review_complete(self) -> Self:
        evidence = (
            self.attorney_reviewed_on,
            self.language_reviewed_on,
            self.review_evidence_ref,
            self.reviewed_text_sha256,
        )
        if self.review_status == "APPROVED" and not all(evidence):
            raise ValueError("gloss_review_incomplete")
        if self.review_status == "UNREVIEWED" and any(evidence):
            raise ValueError("unreviewed_gloss_has_approval")
        if self.review_status == "APPROVED" and self.reviewed_text_sha256 != digest(
            self.text.encode()
        ):
            raise ValueError("gloss_text_changed_after_review")
        return self

    def matches(self, candidate: Candidate, language: DisplayLanguage, as_of: date) -> bool:
        citation = candidate.citation
        return (
            self.review_status == "APPROVED"
            and self.chunk_id == candidate.chunk_id
            and self.source_record_id == citation.record_id
            and self.source_revision == citation.source_revision
            and self.source_language == citation.language
            and self.section_sha256 == citation.section_sha256
            and self.language == language
            and self.attorney_reviewed_on is not None
            and self.language_reviewed_on is not None
            and self.attorney_reviewed_on <= as_of
            and self.language_reviewed_on <= as_of
            and self.attorney_reviewed_on >= citation.retrieved_at.date()
            and self.language_reviewed_on >= citation.retrieved_at.date()
        )


class GlossLibrary(Contract):
    schema_version: Literal["1"] = "1"
    revision: str = Field(min_length=1, max_length=200)
    glosses: tuple[Gloss, ...] = ()

    @model_validator(mode="after")
    def unique_versions(self) -> Self:
        keys = {(item.chunk_id, item.language) for item in self.glosses}
        if len(keys) != len(self.glosses) or len({g.id for g in self.glosses}) != len(self.glosses):
            raise ValueError("duplicate_gloss")
        return self


class DisplayProvision(Contract):
    candidate: Candidate
    gloss: Gloss | None = None
    explanation_status: Literal["reviewed", "text_and_referral"]

    @model_validator(mode="after")
    def bind_gloss(self) -> Self:
        if (self.gloss is not None) != (self.explanation_status == "reviewed"):
            raise ValueError("gloss_display_status_invalid")
        return self


class AnswerDocument(Contract):
    schema_version: Literal["1"] = "1"
    status: Literal[
        "candidates",
        "immediate_escalation",
        "professional_referral",
        "refuse",
        "abstain",
        "review_required",
    ]
    language: DisplayLanguage = "si"
    as_of: date
    decision: TriageDecision
    messages: tuple[str, ...] = ()
    provisions: tuple[DisplayProvision, ...] = ()
    referrals: tuple[Referral, ...] = ()
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_publication(self) -> Self:
        if self.status == "candidates":
            if self.decision.action != "navigate" or len(self.provisions) < 2:
                raise ValueError("answer_requires_multiple_candidates")
        elif self.provisions:
            raise ValueError("blocked_answer_has_provisions")
        if (
            self.status not in {"candidates", "review_required"}
            and self.status != self.decision.action
        ):
            raise ValueError("answer_route_status_mismatch")
        if self.status == "review_required" and (self.messages or self.referrals):
            raise ValueError("unreviewed_response_must_withhold_content")
        if self.status != "review_required" and not self.messages:
            raise ValueError("reviewed_safety_messages_required")
        keys = {
            (p.candidate.citation.instrument_id, p.candidate.citation.section)
            for p in self.provisions
        }
        if len(keys) != len(self.provisions):
            raise ValueError("duplicate_answer_provision")
        for provision in self.provisions:
            if provision.gloss and not provision.gloss.matches(
                provision.candidate, self.language, self.as_of
            ):
                raise ValueError("answer_gloss_not_reviewed_for_version")
        for referral in self.referrals:
            if (
                referral.status != "VERIFIED"
                or referral.verified_on is None
                or referral.review_due is None
                or not referral.verified_on <= self.as_of <= referral.review_due
            ):
                raise ValueError("answer_referral_not_current")
            if referral.kind == "emergency" and not set(referral.urgent_categories).intersection(
                self.decision.urgency
            ):
                raise ValueError("answer_referral_scope_invalid")
        return self


def citation_fields(citation: Citation) -> dict[str, object]:
    """Complete provenance is preserved; the UI may group it but never truncate it."""
    return citation.model_dump(mode="json")
