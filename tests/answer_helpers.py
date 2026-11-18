"""Approvals here refer to clearly synthetic test copy, never the shipped drafts."""

import json
from datetime import date

from conftest import RetrievalContext

from lai.answers.contracts import Gloss, GlossLibrary
from lai.answers.service import AnswerService
from lai.corpus.models import digest
from lai.retrieval.engine import Retriever
from lai.retrieval.models import Candidate, RetrievalPolicy
from lai.triage.contracts import SafetyPolicy
from lai.triage.pipeline import RetrievalNavigation, SafetyNavigator
from lai.triage.referrals import Referral, ReferralRegister
from lai.triage.templates import SafetyTemplates, load_templates

AS_OF = date(2026, 11, 19)


def synthetic_templates() -> SafetyTemplates:
    data = load_templates().model_dump(mode="json")
    for item in data["templates"]:
        item.update(
            text=f"SYNTHETIC reviewed fixture {item['id']} {item['language']}",
            review_status="APPROVED",
            attorney_reviewed_on="2026-11-19",
            language_reviewed_on="2026-11-19",
        )
    return SafetyTemplates.model_validate_json(json.dumps(data))


def service(
    context: RetrievalContext,
    glosses: GlossLibrary | None = None,
    templates: SafetyTemplates | None = None,
) -> AnswerService:
    retriever = Retriever(
        context.catalog,
        context.index,
        context.backend,
        RetrievalPolicy(enabled=True, minimum_dense_similarity=0.05),
    )
    navigator = SafetyNavigator(
        RetrievalNavigation(retriever), SafetyPolicy(research_navigation_enabled=True)
    )
    pending = ReferralRegister(
        revision="synthetic",
        records=(
            Referral(
                id="synthetic-pending",
                kind="legal_aid",
                organisation="SYNTHETIC",
                source_url="https://moj.gov.lk/",
                attempted_on=AS_OF,
                blocker="SYNTHETIC unverified",
            ),
        ),
    )
    return AnswerService(
        navigator,
        context.catalog,
        glosses or GlossLibrary(revision="synthetic-empty"),
        templates or synthetic_templates(),
        pending,
    )


def approved_gloss(candidate: Candidate, language: str = "en") -> Gloss:
    data = {
        "id": f"synthetic-reviewed-{language}",
        "chunk_id": candidate.chunk_id,
        "source_record_id": candidate.citation.record_id,
        "source_revision": candidate.citation.source_revision,
        "source_language": candidate.citation.language,
        "section_sha256": candidate.citation.section_sha256,
        "language": language,
        "text": "SYNTHETIC reviewed explanation",
        "review_status": "APPROVED",
        "attorney_reviewed_on": "2026-11-19",
        "language_reviewed_on": "2026-11-19",
        "review_evidence_ref": "synthetic-review-only",
        "reviewed_text_sha256": digest(b"SYNTHETIC reviewed explanation"),
    }
    return Gloss.model_validate_json(json.dumps(data))
