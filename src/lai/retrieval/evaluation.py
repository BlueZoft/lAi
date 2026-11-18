"""Aggregate retrieval measurements over explicit, non-personal labelled queries."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from lai.corpus.models import Contract, Identifier, Sha256
from lai.retrieval.engine import Retriever
from lai.retrieval.query import LanguageHint


class EvaluationCase(Contract):
    id: Identifier
    query: str = Field(min_length=1, max_length=1024)
    language_hint: LanguageHint | None = None
    relevant_chunk_ids: tuple[Sha256, ...] = Field(min_length=1)


class EvaluationDataset(Contract):
    schema_version: Literal["1"] = "1"
    kind: Literal["synthetic", "legal"]
    cases: tuple[EvaluationCase, ...] = Field(min_length=1, max_length=10000)

    @model_validator(mode="after")
    def unique_cases(self) -> Self:
        if len({case.id for case in self.cases}) != len(self.cases):
            raise ValueError("duplicate_evaluation_case")
        return self


def evaluate(retriever: Retriever, dataset: EvaluationDataset, as_of: date) -> dict[str, object]:
    if retriever.backend.identity.kind == "fake" and dataset.kind != "synthetic":
        raise ValueError("fake_evaluation_requires_synthetic_dataset")
    totals = dict.fromkeys((1, 5, 15), 0.0)
    reciprocal_rank = 0.0
    abstentions = 0
    unsupported = 0
    for case in dataset.cases:
        ranking = retriever.rank_for_evaluation(case.query, as_of, case.language_hint)
        ids = [candidate.chunk_id for candidate in ranking.candidates]
        expected = set(case.relevant_chunk_ids)
        for limit in totals:
            totals[limit] += len(expected.intersection(ids[:limit])) / len(expected)
        first = next((rank for rank, key in enumerate(ids, start=1) if key in expected), None)
        reciprocal_rank += 1 / first if first is not None else 0
        abstentions += len(ids) < retriever.policy.minimum_candidates
        unsupported += "query_unsupported" in ranking.reasons
    count = len(dataset.cases)
    return {
        "dataset_kind": dataset.kind,
        "backend_kind": retriever.backend.identity.kind,
        "backend_name": retriever.backend.identity.name,
        "queries": count,
        "recall_at_1": totals[1] / count,
        "recall_at_5": totals[5] / count,
        "recall_at_15": totals[15] / count,
        "mean_reciprocal_rank": reciprocal_rank / count,
        "abstention_rate": abstentions / count,
        "unsupported_queries": unsupported,
        "minimum_dense_similarity": retriever.policy.minimum_dense_similarity,
        "legal_validation": "UNVERIFIED",
    }
