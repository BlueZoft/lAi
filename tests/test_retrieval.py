import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from conftest import RetrievalContext
from pydantic import ValidationError

from lai.retrieval.catalog import record_chunks
from lai.retrieval.embeddings import FakeEmbedding
from lai.retrieval.engine import Retriever, index_document
from lai.retrieval.index import fuse
from lai.retrieval.models import Candidate, RetrievalPolicy, RetrievalResult, SearchHit, SearchPools

AS_OF = date(2026, 11, 18)


def retriever(context: RetrievalContext, **changes: object) -> Retriever:
    policy = RetrievalPolicy(enabled=True, minimum_dense_similarity=0.05).model_copy(update=changes)
    return Retriever(context.catalog, context.index, context.backend, policy)


def test_default_is_disabled_and_does_no_embedding(
    retrieval_context: RetrievalContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(texts: object) -> None:
        raise AssertionError("Embedding must not run while disabled")

    monkeypatch.setattr(retrieval_context.backend, "embed", forbidden)
    result = Retriever(
        retrieval_context.catalog, retrieval_context.index, retrieval_context.backend
    ).retrieve("catalogue", AS_OF)
    assert result.status == "abstained"
    assert "retrieval_disabled" in result.reasons


def test_hybrid_candidates_have_exact_citations_and_multiple_provisions(
    retrieval_context: RetrievalContext,
) -> None:
    result = retriever(retrieval_context).retrieve("catalogue", AS_OF)
    assert result.status == "candidates"
    assert len(result.candidates) >= 2
    for item in result.candidates:
        assert item.citation.number == "SYNTHETIC-A"
        assert item.citation.year == 2099
        assert item.citation.source_url == "https://example.invalid/synthetic-act"
        assert item.citation.record_id == retrieval_context.record.record_id
        assert item.citation.staleness_warnings
        assert item.citation.amendment_status == "unknown"
    assert "thresholds_unvalidated" in result.warnings


def test_single_or_low_confidence_match_never_becomes_one_answer(
    retrieval_context: RetrievalContext,
) -> None:
    engine = retriever(retrieval_context)
    assert len(engine.rank_for_evaluation("forms", AS_OF).candidates) == 1
    result = engine.retrieve("forms", AS_OF)
    assert result.status == "abstained"
    assert result.candidates == ()
    with pytest.raises(ValidationError, match="multiple_candidates_required"):
        RetrievalResult(status="candidates")
    low = retriever(retrieval_context, minimum_dense_similarity=0.99).retrieve("catalogue", AS_OF)
    assert low.status == "abstained"
    assert "low_similarity" in low.reasons


def test_candidate_contract_rejects_changed_quote_and_section(
    retrieval_context: RetrievalContext,
) -> None:
    result = retriever(retrieval_context).retrieve("catalogue", AS_OF)
    candidate = result.candidates[0]
    data = candidate.model_dump(mode="json") | {"text": "SYNTHETIC tampered quote"}
    with pytest.raises(ValidationError, match="candidate_quote_mismatch"):
        Candidate.model_validate_json(json.dumps(data))
    data = candidate.model_dump(mode="json")
    data["citation"]["section"] = "99"
    with pytest.raises(ValidationError, match="candidate_citation_mismatch"):
        Candidate.model_validate_json(json.dumps(data))


@pytest.mark.safety
def test_corrupted_source_abstains_even_when_index_scores_are_high(
    retrieval_context: RetrievalContext,
) -> None:
    record = retrieval_context.record
    path = retrieval_context.catalog.store.root / "text" / record.manifest.expected_text_sha256
    path.write_bytes(b"SYNTHETIC changed extraction")
    result = retriever(retrieval_context).retrieve("catalogue", AS_OF)
    assert result.status == "abstained" and not result.candidates
    assert "source_or_version_invalid" in result.reasons


def test_backend_failure_is_redacted(
    retrieval_context: RetrievalContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken(texts: object) -> None:
        raise RuntimeError("SYNTHETIC_SENSITIVE_SENTINEL")

    monkeypatch.setattr(retrieval_context.backend, "embed", broken)
    result = retriever(retrieval_context).retrieve("catalogue", AS_OF)
    assert result.status == "abstained"
    assert "SYNTHETIC_SENSITIVE_SENTINEL" not in result.model_dump_json()


def test_model_identity_cannot_be_mixed(retrieval_context: RetrievalContext) -> None:
    with pytest.raises(ValueError, match="embedding_backend_mismatch"):
        Retriever(retrieval_context.catalog, retrieval_context.index, FakeEmbedding())


@pytest.mark.safety
def test_real_source_scope_excludes_synthetic_fixtures(retrieval_context: RetrievalContext) -> None:
    result = retriever(retrieval_context, source_scope="real").retrieve("catalogue", AS_OF)
    assert result.status == "abstained"
    assert "source_scope_mismatch" in result.reasons


def test_dense_and_sparse_rankings_both_contribute(retrieval_context: RetrievalContext) -> None:
    chunks = record_chunks(retrieval_context.record)
    left = SearchHit(chunk=chunks[0], dense_similarity=0.9, sparse_score=1.0)
    right = SearchHit(chunk=chunks[1], dense_similarity=0.8, sparse_score=2.0)
    result = fuse([SearchPools(dense=(left, right), sparse=(right, left))])
    assert result[0].hit.chunk.id == left.chunk.id
    assert result[0].fusion_score == result[1].fusion_score
    assert result[0].hit.dense_similarity == 0.9


def test_duplicate_channel_entries_are_rejected(retrieval_context: RetrievalContext) -> None:
    hit = SearchHit(
        chunk=record_chunks(retrieval_context.record)[0], dense_similarity=0.9, sparse_score=1.0
    )
    with pytest.raises(ValueError, match="index_payload_conflict"):
        fuse([SearchPools(dense=(hit, hit))])


def test_concurrent_reindexing_keeps_one_active_document(
    retrieval_context: RetrievalContext,
) -> None:
    context = retrieval_context
    with ThreadPoolExecutor(max_workers=4) as pool:
        counts = list(
            pool.map(
                lambda _: index_document(
                    context.catalog, context.index, context.backend, context.record.record_id, AS_OF
                ),
                range(8),
            )
        )
    assert counts == [3] * 8
    assert len(context.index.documents) == 1
    assert len(context.index.search(context.backend.embed(["catalogue"])[0]).dense) == 3
