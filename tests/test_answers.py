import json
from datetime import date

import pytest
from answer_helpers import AS_OF, approved_gloss, service
from conftest import RetrievalContext
from pydantic import ValidationError

from lai.answers.contracts import AnswerDocument, Gloss, GlossLibrary
from lai.answers.service import load_glosses
from lai.retrieval.models import RetrievalResult
from lai.triage.contracts import TriageRequest
from lai.triage.templates import load_templates

PAYLOAD = {"scenario": {"text": "documents catalogue", "language": "en"}, "display_language": "en"}
pytestmark = pytest.mark.safety


def test_missing_gloss_preserves_verbatim_sources_and_referral_path(
    retrieval_context: RetrievalContext,
) -> None:
    engine = service(retrieval_context, load_glosses())
    result = engine.answer(PAYLOAD, AS_OF)
    assert result.status == "candidates" and len(result.provisions) == 3
    original = {s.number: s.text for s in retrieval_context.record.parsed.sections}
    for item in result.provisions:
        assert item.candidate.text == original[item.candidate.citation.section]
        assert item.gloss is None and item.explanation_status == "text_and_referral"
        assert item.candidate.citation.staleness_warnings
    assert result.decision.template_ids == ("extractive", "professional")
    assert "reviewed_gloss_unavailable" in result.warnings
    assert "referral_unavailable" in result.warnings
    assert not any(item.review_status == "APPROVED" for item in load_glosses().glosses)


def test_reviewed_gloss_requires_exact_source_version_and_language(
    retrieval_context: RetrievalContext,
) -> None:
    initial = service(retrieval_context).answer(PAYLOAD, AS_OF)
    gloss = approved_gloss(initial.provisions[0].candidate)
    engine = service(retrieval_context, GlossLibrary(revision="synthetic", glosses=(gloss,)))
    result = engine.answer(PAYLOAD, AS_OF)
    assert result.provisions[0].gloss == gloss
    assert all(item.gloss is None for item in result.provisions[1:])
    sinhala = engine.answer(PAYLOAD | {"display_language": "si"}, AS_OF)
    assert all(item.gloss is None for item in sinhala.provisions)
    assert sinhala.provisions[0].candidate.text == initial.provisions[0].candidate.text


@pytest.mark.parametrize(
    "change",
    [
        {"source_record_id": "0" * 64},
        {"source_revision": "SYNTHETIC changed revision"},
        {"source_language": "ta"},
        {"section_sha256": "0" * 64},
        {"chunk_id": "0" * 64},
        {"attorney_reviewed_on": "2027-01-01"},
        {"language_reviewed_on": "2020-01-01"},
    ],
)
def test_changed_or_not_yet_reviewed_versions_do_not_display_glosses(
    retrieval_context: RetrievalContext, change: dict[str, object]
) -> None:
    candidate = service(retrieval_context).answer(PAYLOAD, AS_OF).provisions[0].candidate
    data = approved_gloss(candidate).model_dump(mode="json") | change
    gloss = Gloss.model_validate_json(json.dumps(data))
    result = service(
        retrieval_context, GlossLibrary(revision="synthetic", glosses=(gloss,))
    ).answer(PAYLOAD, AS_OF)
    assert all(item.gloss is None for item in result.provisions)


def test_approval_cannot_survive_changed_gloss_text(retrieval_context: RetrievalContext) -> None:
    candidate = service(retrieval_context).answer(PAYLOAD, AS_OF).provisions[0].candidate
    gloss = approved_gloss(candidate)
    with pytest.raises(ValidationError, match="gloss_text_changed_after_review"):
        Gloss.model_validate_json(
            json.dumps(gloss.model_dump(mode="json") | {"text": "SYNTHETIC changed"})
        )
    with pytest.raises(ValidationError, match="duplicate_gloss"):
        GlossLibrary(revision="synthetic", glosses=(gloss, gloss))
    changed = gloss.model_copy(update={"text": "SYNTHETIC bypass attempt"})
    with pytest.raises(ValidationError, match="gloss_text_changed_after_review"):
        service(retrieval_context, GlossLibrary(revision="synthetic", glosses=(changed,)))


def test_unreviewed_copy_stops_work_before_embedding(
    retrieval_context: RetrievalContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = service(retrieval_context, templates=load_templates())

    def forbidden(texts: object) -> None:
        raise AssertionError("Downstream must not execute before copy review")

    monkeypatch.setattr(retrieval_context.backend, "embed", forbidden)
    result = engine.answer(PAYLOAD, AS_OF)
    assert result.status == "review_required"
    assert not result.provisions and not result.messages and not result.referrals


def test_source_change_after_retrieval_blocks_every_provision(
    retrieval_context: RetrievalContext,
) -> None:
    engine = service(retrieval_context)
    downstream = engine.navigator.downstream

    class ChangeAfterRetrieval:
        def run(self, request: TriageRequest, as_of: date) -> RetrievalResult:
            result = downstream.run(request, as_of)
            path = (
                retrieval_context.catalog.store.root
                / "text"
                / retrieval_context.record.manifest.expected_text_sha256
            )
            path.write_bytes(b"SYNTHETIC changed source after retrieval")
            return result

    engine.navigator.downstream = ChangeAfterRetrieval()
    result = engine.answer(PAYLOAD, AS_OF)
    assert result.status == "abstain" and not result.provisions
    assert result.decision.reasons == ("source_changed_or_invalid",)


def test_citation_label_tampering_is_rejected_before_display(
    retrieval_context: RetrievalContext,
) -> None:
    engine = service(retrieval_context)
    downstream = engine.navigator.downstream

    class Tamper:
        def run(self, request: TriageRequest, as_of: date) -> RetrievalResult:
            result = downstream.run(request, as_of)
            first = result.candidates[0]
            bad = first.model_copy(
                update={"citation": first.citation.model_copy(update={"number": "SYNTHETIC WRONG"})}
            )
            return result.model_copy(update={"candidates": (bad,) + result.candidates[1:]})

    engine.navigator.downstream = Tamper()
    result = engine.answer(PAYLOAD, AS_OF)
    assert result.status == "abstain" and not result.provisions
    assert "SYNTHETIC WRONG" not in result.model_dump_json()


def test_single_match_abstains_and_query_facts_are_not_echoed(
    retrieval_context: RetrievalContext,
) -> None:
    engine = service(retrieval_context)
    result = engine.answer(
        {"scenario": {"text": "forms PRIVATE_SENTINEL", "language": "en"}}, AS_OF
    )
    assert result.status == "abstain" and not result.provisions
    assert "PRIVATE_SENTINEL" not in result.model_dump_json()


def test_public_contract_rejects_single_or_blocked_quotes(
    retrieval_context: RetrievalContext,
) -> None:
    result = service(retrieval_context).answer(PAYLOAD, AS_OF)
    data = result.model_dump(mode="json")
    data["provisions"] = data["provisions"][:1]
    with pytest.raises(ValidationError, match="answer_requires_multiple_candidates"):
        AnswerDocument.model_validate_json(json.dumps(data))
    data["status"] = "review_required"
    with pytest.raises(ValidationError, match="blocked_answer_has_provisions"):
        AnswerDocument.model_validate_json(json.dumps(data))
    data["provisions"] = []
    data["status"] = "refuse"
    with pytest.raises(ValidationError, match="answer_route_status_mismatch"):
        AnswerDocument.model_validate_json(json.dumps(data))
