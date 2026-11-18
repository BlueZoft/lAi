"""Shared index contract, offline fake index and reciprocal-rank fusion."""

from collections.abc import Sequence
from threading import RLock
from typing import Protocol

from lai.corpus.models import IngestionRecord
from lai.retrieval.catalog import document_key, record_chunks
from lai.retrieval.embeddings import dense_similarity, sparse_similarity
from lai.retrieval.models import (
    BackendIdentity,
    Embedding,
    EncodedSection,
    RankedSection,
    SearchHit,
    SearchPools,
)


class RetrievalIndex(Protocol):
    identity: BackendIdentity

    def replace_document(
        self, record: IngestionRecord, sections: Sequence[EncodedSection]
    ) -> None: ...

    def search(self, vector: Embedding, limit: int = 15) -> SearchPools: ...


def check_sections(
    identity: BackendIdentity, record: IngestionRecord, sections: Sequence[EncodedSection]
) -> None:
    if not record.eligible_for_retrieval and sections:
        raise ValueError("quarantined_document_has_chunks")
    if identity.kind == "fake" and not record.manifest.instrument.synthetic:
        raise ValueError("fake_backend_requires_synthetic_source")
    if any(item.chunk.record_id != record.record_id for item in sections):
        raise ValueError("indexed_record_mismatch")
    if any(len(item.vector.dense) != identity.dimensions for item in sections):
        raise ValueError("embedding_dimension_mismatch")
    if len({item.chunk.id for item in sections}) != len(sections):
        raise ValueError("duplicate_indexed_section")
    allowed = {chunk.id: chunk for chunk in record_chunks(record)}
    if any(allowed.get(item.chunk.id) != item.chunk for item in sections):
        raise ValueError("indexed_chunk_source_mismatch")


class MemoryIndex:
    def __init__(self, identity: BackendIdentity):
        self.identity = identity
        self.documents: dict[str, tuple[EncodedSection, ...]] = {}
        self.records: dict[str, IngestionRecord] = {}
        self.lock = RLock()

    def replace_document(self, record: IngestionRecord, sections: Sequence[EncodedSection]) -> None:
        check_sections(self.identity, record, sections)
        prepared = tuple(
            EncodedSection(chunk=item.chunk, vector=item.vector.normalised()) for item in sections
        )
        with self.lock:
            self.documents[document_key(record)] = prepared
            self.records[record.record_id] = record

    def search(self, vector: Embedding, limit: int = 15) -> SearchPools:
        if len(vector.dense) != self.identity.dimensions or not 1 <= limit <= 100:
            raise ValueError("search_parameters_invalid")
        query = vector.normalised()
        with self.lock:
            documents = tuple(self.documents.values())
        hits = [
            SearchHit(
                chunk=item.chunk,
                dense_similarity=dense_similarity(query, item.vector),
                sparse_score=sparse_similarity(query, item.vector),
            )
            for document in documents
            for item in document
        ]
        return SearchPools(
            dense=tuple(
                sorted(hits, key=lambda hit: (-hit.dense_similarity, hit.chunk.id))[:limit]
            ),
            sparse=tuple(
                sorted(
                    (hit for hit in hits if hit.sparse_score > 0),
                    key=lambda hit: (-hit.sparse_score, hit.chunk.id),
                )[:limit]
            ),
        )


def fuse(pools: Sequence[SearchPools], constant: int = 60) -> tuple[RankedSection, ...]:
    hits: dict[str, SearchHit] = {}
    scores: dict[str, float] = {}
    for pool in pools:
        for channel in (pool.dense, pool.sparse):
            seen: set[str] = set()
            for rank, hit in enumerate(channel, start=1):
                key = hit.chunk.id
                if key in seen or (key in hits and hits[key].chunk != hit.chunk):
                    raise ValueError("index_payload_conflict")
                seen.add(key)
                previous = hits.get(key, hit)
                hits[key] = SearchHit(
                    chunk=hit.chunk,
                    dense_similarity=max(previous.dense_similarity, hit.dense_similarity),
                    sparse_score=max(previous.sparse_score, hit.sparse_score),
                )
                scores[key] = scores.get(key, 0) + 1 / (constant + rank)
    ranked = [RankedSection(hit=hits[key], fusion_score=score) for key, score in scores.items()]
    return tuple(
        sorted(
            ranked,
            key=lambda item: (
                -item.fusion_score,
                -item.hit.dense_similarity,
                -item.hit.sparse_score,
                item.hit.chunk.id,
            ),
        )
    )
