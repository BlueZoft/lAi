"""Retrieval contracts. Ranking scores carry no legal correctness probability."""

import math
from typing import Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from lai.corpus.models import Contract, Identifier, Language, Sha256, content_id, digest


class BackendIdentity(Contract):
    name: str = Field(min_length=1, max_length=200)
    dimensions: int = Field(ge=8, le=1024)
    kind: Literal["fake", "bge_m3"]


class Embedding(Contract):
    dense: tuple[float, ...] = Field(min_length=8, max_length=1024)
    sparse: dict[str, float] = Field(default_factory=dict, max_length=8192)

    @model_validator(mode="after")
    def validate_values(self) -> Self:
        if any(not math.isfinite(value) for value in self.dense):
            raise ValueError("nonfinite_dense_vector")
        norm = math.sqrt(sum(value * value for value in self.dense))
        if not math.isfinite(norm) or norm < 1e-12:
            raise ValueError("zero_or_invalid_dense_vector")
        if any(not key or len(key) > 200 for key in self.sparse):
            raise ValueError("invalid_sparse_key")
        if any(not math.isfinite(value) or value < 0 for value in self.sparse.values()):
            raise ValueError("invalid_sparse_weight")
        return self

    def normalised(self) -> "Embedding":
        norm = math.sqrt(sum(value * value for value in self.dense))
        return Embedding(
            dense=tuple(value / norm for value in self.dense), sparse=self.sparse.copy()
        )


class SectionChunk(Contract):
    id: Sha256
    document_key: Sha256
    record_id: Sha256
    section_number: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str = Field(min_length=1)
    text_sha256: Sha256
    language: Language
    instrument_id: Identifier
    synthetic: bool

    @model_validator(mode="after")
    def validate_text(self) -> Self:
        if (
            self.end - self.start != len(self.text)
            or digest(self.text.encode()) != self.text_sha256
        ):
            raise ValueError("chunk_anchor_invalid")
        return self


class EncodedSection(Contract):
    chunk: SectionChunk
    vector: Embedding


class SearchHit(Contract):
    chunk: SectionChunk
    dense_similarity: float = Field(ge=-1.00001, le=1.00001, allow_inf_nan=False)
    sparse_score: float = Field(ge=0, allow_inf_nan=False)


class SearchPools(Contract):
    dense: tuple[SearchHit, ...] = ()
    sparse: tuple[SearchHit, ...] = ()


class RankedSection(Contract):
    hit: SearchHit
    fusion_score: float = Field(gt=0, allow_inf_nan=False)


class Citation(Contract):
    record_id: Sha256
    instrument_type: str
    instrument_id: Identifier
    number: str = Field(min_length=1)
    year: int
    section: str
    language: Language
    source_url: str
    canonical_url: str | None
    retrieved_at: AwareDatetime
    source_revision: str
    raw_sha256: Sha256
    text_sha256: Sha256
    section_sha256: Sha256
    start: int
    end: int
    amendment_status: Literal["unknown", "amendment_recorded", "repeal_recorded"]
    commencement_status: Literal["unknown", "commencement_recorded"]
    staleness_warnings: tuple[str, ...] = Field(min_length=1)


class Candidate(Contract):
    chunk_id: Sha256
    text: str
    citation: Citation
    dense_similarity: float
    sparse_score: float
    fusion_score: float

    @model_validator(mode="after")
    def bind_citation(self) -> Self:
        citation = self.citation
        if (
            citation.end - citation.start != len(self.text)
            or digest(self.text.encode()) != citation.section_sha256
        ):
            raise ValueError("candidate_quote_mismatch")
        identity = {
            "raw_sha256": citation.raw_sha256,
            "extracted_text_sha256": citation.text_sha256,
            "instrument_id": citation.instrument_id,
            "language": citation.language,
            "section_number": citation.section,
            "start": citation.start,
            "end": citation.end,
            "text_sha256": citation.section_sha256,
        }
        if content_id(identity) != self.chunk_id:
            raise ValueError("candidate_citation_mismatch")
        return self


class RetrievalResult(Contract):
    status: Literal["candidates", "abstained"]
    candidates: tuple[Candidate, ...] = ()
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ("thresholds_unvalidated",)

    @model_validator(mode="after")
    def multiple_candidates(self) -> Self:
        if self.status == "candidates" and len(self.candidates) < 2:
            raise ValueError("multiple_candidates_required")
        if self.status == "abstained" and self.candidates:
            raise ValueError("abstention_must_be_empty")
        keys = {(item.citation.instrument_id, item.citation.section) for item in self.candidates}
        if len(keys) != len(self.candidates):
            raise ValueError("duplicate_logical_provision")
        return self


class EvaluationRanking(Contract):
    candidates: tuple[Candidate, ...] = ()
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ("thresholds_unvalidated",)


class RetrievalPolicy(Contract):
    enabled: bool = False
    source_scope: Literal["synthetic", "real"] = "synthetic"
    minimum_candidates: int = Field(default=2, ge=2, le=15)
    maximum_candidates: int = Field(default=5, ge=2, le=15)
    pool_size: int = Field(default=15, ge=2, le=100)
    minimum_dense_similarity: float = Field(default=0.5, ge=0, le=1)
    acquisition_warning_days: int = Field(default=90, ge=1)

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        if (
            self.minimum_candidates > self.maximum_candidates
            or self.maximum_candidates > self.pool_size
        ):
            raise ValueError("retrieval_limits_invalid")
        return self
