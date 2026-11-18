import math
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import ValidationError

from lai.retrieval.embeddings import BGEM3Embedding, FakeEmbedding, load_local_bge
from lai.retrieval.model_files import file_digest, verify_model_files
from lai.retrieval.models import Embedding


class StubFlagEncoder:
    def __init__(self, length: int = 3):
        self.length, self.encode_calls = length, 0

    def tokenizer(
        self, texts: list[str], **kwargs: object
    ) -> Mapping[str, Sequence[Sequence[int]]]:
        assert kwargs["truncation"] is False
        return {"input_ids": [[1] * self.length for _ in texts]}

    def encode(self, texts: list[str], **kwargs: object) -> Mapping[str, object]:
        self.encode_calls += 1
        assert kwargs["return_dense"] is True and kwargs["return_sparse"] is True
        assert kwargs["return_colbert_vecs"] is False
        return {
            "dense_vecs": [[1.0] + [0.0] * 1023 for _ in texts],
            "lexical_weights": [{"42": 0.5} for _ in texts],
        }


def test_fake_is_stable_and_its_alias_configuration_has_identity() -> None:
    backend = FakeEmbedding(aliases={"form": "forms"})
    vectors = backend.embed(["form", "forms"])
    assert vectors[0] == vectors[1]
    assert vectors == FakeEmbedding(aliases={"form": "forms"}).embed(["form", "forms"])
    assert backend.identity != FakeEmbedding().identity
    assert math.isclose(sum(value * value for value in vectors[0].dense), 1)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_dense_vectors_are_rejected(bad: float) -> None:
    with pytest.raises(ValidationError):
        Embedding(dense=(bad,) + (0.0,) * 7)


def test_zero_vectors_and_negative_sparse_weights_are_rejected() -> None:
    with pytest.raises(ValidationError, match="zero_or_invalid_dense_vector"):
        Embedding(dense=(0.0,) * 8)
    with pytest.raises(ValidationError, match="invalid_sparse_weight"):
        Embedding(dense=(1.0,) + (0.0,) * 7, sparse={"synthetic": -1.0})


def test_local_adapter_validates_dense_and_sparse_contract() -> None:
    encoder = StubFlagEncoder()
    backend = BGEM3Embedding(encoder, "synthetic-weights-revision")
    vectors = backend.embed(["SYNTHETIC forms"])
    assert backend.identity.dimensions == 1024
    assert vectors[0].sparse == {"42": 0.5}
    assert encoder.encode_calls == 1


def test_oversized_sections_are_rejected_before_encoder_truncation() -> None:
    encoder = StubFlagEncoder(length=8193)
    with pytest.raises(ValueError, match="embedding_context_limit"):
        BGEM3Embedding(encoder, "synthetic").embed(["SYNTHETIC long section"])
    assert encoder.encode_calls == 0


def test_local_loader_sets_offline_flags_and_disables_remote_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = ModuleType("FlagEmbedding")
    seen: dict[str, object] = {}

    def factory(path: str, **kwargs: object) -> StubFlagEncoder:
        seen.update(kwargs)
        seen["path"] = path
        return StubFlagEncoder()

    module.__dict__["BGEM3FlagModel"] = factory
    monkeypatch.setitem(sys.modules, "FlagEmbedding", module)
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "0")
    (tmp_path / "config.json").write_text("{}")
    backend = load_local_bge(tmp_path, "synthetic")
    assert seen["trust_remote_code"] is False
    assert seen["devices"] == ["cpu"]
    import os

    assert os.environ["HF_HUB_OFFLINE"] == os.environ["TRANSFORMERS_OFFLINE"] == "1"
    assert backend.embed(["SYNTHETIC input"])


def test_model_path_is_required_before_optional_sdk_import(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="local_model_missing"):
        load_local_bge(tmp_path / "missing", "synthetic")


def test_model_checksum_manifest_detects_changed_file_and_wrong_revision(tmp_path: Path) -> None:
    import json

    path = tmp_path / "synthetic-config.json"
    path.write_text('{"synthetic": true}')
    (tmp_path / "lai-model-manifest.json").write_text(
        json.dumps(
            {
                "revision": "synthetic",
                "files": {path.name: file_digest(path)},
            }
        )
    )
    verify_model_files(tmp_path, "synthetic")
    with pytest.raises(ValueError, match="model_manifest_invalid"):
        verify_model_files(tmp_path, "wrong-synthetic-revision")
    path.write_text('{"synthetic": false}')
    with pytest.raises(ValueError, match="model_file_checksum_mismatch"):
        verify_model_files(tmp_path, "synthetic")
