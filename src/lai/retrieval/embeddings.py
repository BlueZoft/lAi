"""Deterministic fake and local BGE-M3 adapter. No model download occurs here."""

import hashlib
import importlib
import math
import os
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Protocol, cast

from lai.corpus.models import content_id
from lai.retrieval.model_files import verify_model_files
from lai.retrieval.models import BackendIdentity, Embedding
from lai.retrieval.query import tokens


class EmbeddingBackend(Protocol):
    identity: BackendIdentity

    def embed(self, texts: Sequence[str]) -> tuple[Embedding, ...]: ...


class FakeEmbedding:
    def __init__(self, dimensions: int = 1024, aliases: Mapping[str, str] | None = None):
        self.aliases = MappingProxyType(dict(aliases or {}))
        self.identity = BackendIdentity(
            name=f"fake-hash-v1:{content_id(dict(self.aliases))}",
            dimensions=dimensions,
            kind="fake",
        )

    def embed(self, texts: Sequence[str]) -> tuple[Embedding, ...]:
        result: list[Embedding] = []
        for text in texts:
            counts = Counter(self.aliases.get(word, word) for word in tokens(text))
            if not counts:
                raise ValueError("empty_embedding_input")
            dense = [0.0] * self.identity.dimensions
            for word, count in counts.items():
                hashed = hashlib.sha256(word.encode()).digest()
                position = int.from_bytes(hashed[:4]) % self.identity.dimensions
                dense[position] += count
            sparse = {word: float(count) for word, count in counts.items()}
            result.append(Embedding(dense=tuple(dense), sparse=sparse).normalised())
        return tuple(result)


class LocalFlagEncoder(Protocol):
    def tokenizer(
        self, texts: list[str], **kwargs: object
    ) -> Mapping[str, Sequence[Sequence[int]]]: ...

    def encode(self, texts: list[str], **kwargs: object) -> Mapping[str, object]: ...


class BGEM3Embedding:
    def __init__(self, encoder: LocalFlagEncoder, revision: str):
        self.encoder = encoder
        self.identity = BackendIdentity(name=f"bge-m3:{revision}", dimensions=1024, kind="bge_m3")

    def embed(self, texts: Sequence[str]) -> tuple[Embedding, ...]:
        lengths = self.encoder.tokenizer(list(texts), truncation=False, add_special_tokens=True)
        input_ids = lengths["input_ids"]
        if len(input_ids) != len(texts) or any(len(item) > 8192 for item in input_ids):
            raise ValueError("embedding_context_limit")
        output = self.encoder.encode(
            list(texts),
            batch_size=1,
            max_length=8192,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
            show_progress_bar=False,
        )
        dense = output["dense_vecs"]
        converter = getattr(dense, "tolist", None)
        if callable(converter):
            dense = converter()
        sparse = output["lexical_weights"]
        if (
            not isinstance(dense, list)
            or not isinstance(sparse, list)
            or len(dense) != len(texts)
            or len(sparse) != len(texts)
        ):
            raise ValueError("embedding_output_invalid")
        vectors: list[Embedding] = []
        for row, weights in zip(dense, sparse, strict=True):
            if not isinstance(row, (list, tuple)) or not isinstance(weights, dict):
                raise ValueError("embedding_output_invalid")
            vector = Embedding(
                dense=tuple(row), sparse={str(key): value for key, value in weights.items()}
            )
            if len(vector.dense) != 1024:
                raise ValueError("embedding_dimension_mismatch")
            vectors.append(vector.normalised())
        return tuple(vectors)


def load_local_bge(path: Path, revision: str, device: str = "cpu") -> BGEM3Embedding:
    if not path.is_dir() or not (path / "config.json").is_file():
        raise ValueError("local_model_missing")
    verify_model_files(path, revision)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    module = importlib.import_module("FlagEmbedding")
    encoder = module.BGEM3FlagModel(
        str(path.resolve()), devices=[device], use_fp16=False, trust_remote_code=False
    )
    return BGEM3Embedding(cast(LocalFlagEncoder, encoder), revision)


def dense_similarity(left: Embedding, right: Embedding) -> float:
    if len(left.dense) != len(right.dense):
        raise ValueError("embedding_dimension_mismatch")
    value = sum(a * b for a, b in zip(left.dense, right.dense, strict=True))
    if not math.isfinite(value):
        raise ValueError("invalid_dense_similarity")
    return max(-1.0, min(1.0, value))


def sparse_similarity(left: Embedding, right: Embedding) -> float:
    return sum(value * right.sparse.get(key, 0.0) for key, value in left.sparse.items())
