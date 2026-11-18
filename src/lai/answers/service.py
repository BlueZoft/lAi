"""No generation. Safety gate, reviewed fixed copy, source recheck, exact text and referrals."""

from collections.abc import Mapping
from datetime import date
from importlib.resources import files

from pydantic import ValidationError

from lai.answers.contracts import (
    AnswerDocument,
    AnswerRequest,
    DisplayLanguage,
    DisplayProvision,
    GlossLibrary,
)
from lai.corpus.models import Source
from lai.retrieval.catalog import SourceCatalog, record_chunks
from lai.retrieval.models import Candidate
from lai.triage.contracts import TriageDecision
from lai.triage.pipeline import SafetyNavigator
from lai.triage.referrals import ReferralRegister, active_referrals, load_referrals
from lai.triage.rules import decide
from lai.triage.templates import SafetyTemplates, approved_messages, load_templates


def load_glosses() -> GlossLibrary:
    return GlossLibrary.model_validate_json(
        files("lai.answers").joinpath("data/glosses.json").read_bytes()
    )


class AnswerService:
    def __init__(
        self,
        navigator: SafetyNavigator,
        catalog: SourceCatalog | None = None,
        glosses: GlossLibrary | None = None,
        templates: SafetyTemplates | None = None,
        referrals: ReferralRegister | None = None,
    ):
        self.navigator, self.catalog = navigator, catalog
        self.glosses = glosses if glosses is not None else load_glosses()
        self.templates = templates if templates is not None else load_templates()
        self.referrals = referrals if referrals is not None else load_referrals()
        self.glosses = GlossLibrary.model_validate_json(self.glosses.model_dump_json())
        self.templates = SafetyTemplates.model_validate_json(self.templates.model_dump_json())
        self.referrals = ReferralRegister.model_validate_json(self.referrals.model_dump_json())

    def copy_ready(self, language: DisplayLanguage, as_of: date) -> bool:
        return all(
            item.review_status == "APPROVED"
            and item.attorney_reviewed_on is not None
            and item.language_reviewed_on is not None
            and item.attorney_reviewed_on <= as_of
            and item.language_reviewed_on <= as_of
            for item in self.templates.templates
            if item.language == language
        )

    def blocked(
        self,
        decision: TriageDecision,
        language: DisplayLanguage,
        as_of: date,
        region: str | None = None,
    ) -> AnswerDocument:
        messages = approved_messages(decision, language, as_of, self.templates)
        if not messages:
            return AnswerDocument(
                status="review_required",
                language=language,
                as_of=as_of,
                decision=decision,
                warnings=("safety_copy_unreviewed",),
            )
        kinds = tuple(kind for kind in decision.referral_kinds if kind != "regional" or region)
        referrals = active_referrals(
            kinds, as_of, self.referrals, urgency=decision.urgency, region=region
        )
        return AnswerDocument(
            status=decision.action if decision.action != "navigate" else "abstain",
            language=language,
            as_of=as_of,
            decision=decision,
            messages=messages,
            referrals=referrals,
            warnings=() if referrals else ("referral_unavailable",),
        )

    def revalidate(self, candidate: Candidate, as_of: date) -> None:
        if self.catalog is None:
            raise ValueError("source_catalog_unavailable")
        record = self.catalog.store.load(candidate.citation.record_id)
        chunk = next(
            (chunk for chunk in record_chunks(record) if chunk.id == candidate.chunk_id), None
        )
        if chunk is None or chunk.text != candidate.text:
            raise ValueError("answer_quote_not_in_source")
        fresh = self.catalog.resolve(chunk, as_of)
        if fresh != candidate.citation:
            raise ValueError("answer_citation_changed")
        Source.public_source_url(fresh.source_url)
        if fresh.canonical_url:
            Source.public_source_url(fresh.canonical_url)

    def answer(self, payload: object, as_of: date) -> AnswerDocument:
        raw = payload if isinstance(payload, Mapping) else {}
        scenario = raw.get("scenario", {})
        language: DisplayLanguage = "en" if raw.get("display_language") == "en" else "si"
        preliminary = decide(scenario, self.navigator.policy)
        if preliminary.action == "immediate_escalation":
            # The same T4 entry contract handles urgent requests, including malformed envelopes.
            outcome = self.navigator.handle(scenario, as_of)
            return self.blocked(outcome.decision, language, as_of)
        try:
            request = AnswerRequest.model_validate(payload)
        except ValidationError:
            decision = TriageDecision(
                action="abstain",
                reasons=("invalid_answer_request",),
                limitation_warning=preliminary.limitation_warning,
                template_ids=("abstain", "limitation")
                if preliminary.limitation_warning
                else ("abstain",),
            )
            return self.blocked(decision, language, as_of)
        if preliminary.action != "navigate":
            outcome = self.navigator.handle(request.scenario.model_dump(), as_of)
            return self.blocked(outcome.decision, request.display_language, as_of, request.region)
        # Check all possible fixed safety messages before permitting downstream work.
        if not self.copy_ready(request.display_language, as_of):
            return AnswerDocument(
                status="review_required",
                language=request.display_language,
                as_of=as_of,
                decision=preliminary,
                warnings=("safety_copy_unreviewed",),
            )
        outcome = self.navigator.handle(request.scenario.model_dump(), as_of)
        if outcome.retrieval is None:
            return self.blocked(outcome.decision, request.display_language, as_of, request.region)
        try:
            provisions: list[DisplayProvision] = []
            for candidate in outcome.retrieval.candidates:
                self.revalidate(candidate, as_of)
                gloss = next(
                    (
                        g
                        for g in self.glosses.glosses
                        if g.matches(candidate, request.display_language, as_of)
                    ),
                    None,
                )
                provisions.append(
                    DisplayProvision(
                        candidate=candidate,
                        gloss=gloss,
                        explanation_status="reviewed" if gloss else "text_and_referral",
                    )
                )
        except (OSError, ValueError):
            return self.blocked(
                TriageDecision(
                    action="abstain",
                    reasons=("source_changed_or_invalid",),
                    template_ids=("abstain",),
                ),
                request.display_language,
                as_of,
            )
        decision = outcome.decision
        if any(p.gloss is None for p in provisions):
            decision = decision.model_copy(update={"template_ids": ("extractive", "professional")})
        messages = approved_messages(decision, request.display_language, as_of, self.templates)
        referrals = active_referrals(("legal_aid", "attorney_review"), as_of, self.referrals)
        allowed_warnings = {
            "thresholds_unvalidated",
            "mixed_script",
            "transliteration_requires_measurement",
        }
        warnings = set(outcome.retrieval.warnings).intersection(allowed_warnings)
        if any(p.gloss is None for p in provisions):
            warnings.add("reviewed_gloss_unavailable")
        if not referrals:
            warnings.add("referral_unavailable")
        return AnswerDocument(
            status="candidates",
            language=request.display_language,
            as_of=as_of,
            decision=decision,
            messages=messages,
            provisions=tuple(provisions),
            referrals=referrals,
            warnings=tuple(sorted(warnings)),
        )
