"""Private research retrieval. Public request routing is introduced after T4 triage."""

from collections.abc import Sequence
from datetime import date

from lai.corpus.ingest import select_canonical
from lai.corpus.models import IngestionRecord
from lai.retrieval.catalog import SourceCatalog, document_key
from lai.retrieval.embeddings import EmbeddingBackend
from lai.retrieval.index import RetrievalIndex, fuse
from lai.retrieval.models import (
    Candidate,
    EncodedSection,
    EvaluationRanking,
    RetrievalPolicy,
    RetrievalResult,
)
from lai.retrieval.query import LanguageHint, Transliterator, plan_query


def index_document(
    catalog: SourceCatalog,
    index: RetrievalIndex,
    backend: EmbeddingBackend,
    record_id: str,
    as_of: date,
) -> int:
    if index.identity != backend.identity:
        raise ValueError("embedding_backend_mismatch")
    record, chunks = catalog.eligible_chunks(record_id, as_of)
    if backend.identity.kind == "fake" and not record.manifest.instrument.synthetic:
        raise ValueError("fake_backend_requires_synthetic_source")
    vectors = backend.embed([chunk.text for chunk in chunks]) if chunks else ()
    if len(vectors) != len(chunks):
        raise ValueError("embedding_output_invalid")
    sections = [
        EncodedSection(chunk=chunk, vector=vector.normalised())
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    index.replace_document(record, sections)
    return len(sections)


def index_selected_records(
    catalog: SourceCatalog,
    index: RetrievalIndex,
    backend: EmbeddingBackend,
    record_ids: Sequence[str],
    as_of: date,
) -> int:
    groups: dict[str, list[IngestionRecord]] = {}
    for record_id in dict.fromkeys(record_ids):
        record = catalog.store.load(record_id)
        groups.setdefault(document_key(record), []).append(record)
    selected = [select_canonical(group).record_id for group in groups.values()]
    return sum(index_document(catalog, index, backend, key, as_of) for key in selected)


class Retriever:
    def __init__(
        self,
        catalog: SourceCatalog,
        index: RetrievalIndex,
        backend: EmbeddingBackend,
        policy: RetrievalPolicy | None = None,
        transliterator: Transliterator | None = None,
    ):
        if index.identity != backend.identity:
            raise ValueError("embedding_backend_mismatch")
        self.catalog, self.index, self.backend = catalog, index, backend
        self.policy = policy or RetrievalPolicy()
        self.transliterator = transliterator

    def retrieve(self, text: str, as_of: date, hint: LanguageHint | None = None) -> RetrievalResult:
        ranking = self.rank_for_evaluation(text, as_of, hint)
        if len(ranking.candidates) < self.policy.minimum_candidates:
            reasons = set(ranking.reasons) | {"insufficient_candidates"}
            return RetrievalResult(
                status="abstained", reasons=tuple(sorted(reasons)), warnings=ranking.warnings
            )
        return RetrievalResult(
            status="candidates",
            candidates=ranking.candidates[: self.policy.maximum_candidates],
            warnings=ranking.warnings,
        )

    def rank_for_evaluation(
        self,
        text: str,
        as_of: date,
        hint: LanguageHint | None = None,
    ) -> EvaluationRanking:
        if not self.policy.enabled:
            return EvaluationRanking(reasons=("retrieval_disabled",))
        try:
            plan = plan_query(text, hint, self.transliterator)
        except ValueError:
            return EvaluationRanking(reasons=("query_unsupported",))
        try:
            vectors = self.backend.embed(plan.variants)
            if len(vectors) != len(plan.variants):
                raise ValueError("embedding_output_invalid")
            pools = [
                self.index.search(vector.normalised(), self.policy.pool_size) for vector in vectors
            ]
            ranked = fuse(pools)
        except Exception:
            return EvaluationRanking(reasons=("retrieval_backend_unavailable",))
        candidates: list[Candidate] = []
        seen: set[tuple[str, str]] = set()
        rejected: set[str] = set()
        for item in ranked:
            hit = item.hit
            if hit.dense_similarity < self.policy.minimum_dense_similarity:
                rejected.add("low_similarity")
                continue
            if hit.chunk.synthetic != (self.policy.source_scope == "synthetic"):
                rejected.add("source_scope_mismatch")
                continue
            try:
                citation = self.catalog.resolve(
                    hit.chunk, as_of, self.policy.acquisition_warning_days
                )
            except (OSError, ValueError):
                rejected.add("source_or_version_invalid")
                continue
            key = (citation.instrument_id, citation.section)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                Candidate(
                    chunk_id=hit.chunk.id,
                    text=hit.chunk.text,
                    citation=citation,
                    dense_similarity=hit.dense_similarity,
                    sparse_score=hit.sparse_score,
                    fusion_score=item.fusion_score,
                )
            )
            if len(candidates) == self.policy.pool_size:
                break
        warnings = ("thresholds_unvalidated",) + plan.warnings
        return EvaluationRanking(
            candidates=tuple(candidates), reasons=tuple(sorted(rejected)), warnings=warnings
        )
