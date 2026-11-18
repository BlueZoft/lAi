from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from lai.corpus.graph import VersionGraph, document_nodes
from lai.corpus.ingest import ingest_document
from lai.corpus.models import IngestionRecord, SourceManifest
from lai.corpus.store import CorpusStore
from lai.retrieval.catalog import SourceCatalog
from lai.retrieval.embeddings import FakeEmbedding
from lai.retrieval.engine import index_document
from lai.retrieval.index import MemoryIndex

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def source_bytes() -> bytes:
    return (FIXTURES / "synthetic-act.txt").read_bytes()


@pytest.fixture
def source_manifest() -> SourceManifest:
    return SourceManifest.model_validate_json(
        (FIXTURES / "synthetic-act.manifest.json").read_bytes()
    )


@pytest.fixture
def ingested_record(source_manifest: SourceManifest, source_bytes: bytes) -> IngestionRecord:
    return ingest_document(source_manifest, source_bytes, source_bytes)


@dataclass
class RetrievalContext:
    catalog: SourceCatalog
    index: MemoryIndex
    backend: FakeEmbedding
    record: IngestionRecord


@pytest.fixture
def retrieval_context(
    tmp_path: Path,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> RetrievalContext:
    store = CorpusStore(tmp_path / "corpus")
    record = store.ingest(source_manifest, source_bytes, source_bytes)
    catalog = SourceCatalog(store, VersionGraph(nodes=document_nodes(record)))
    backend = FakeEmbedding(aliases={"form": "forms"})
    index = MemoryIndex(backend.identity)
    index_document(catalog, index, backend, record.record_id, date(2026, 11, 18))
    return RetrievalContext(catalog, index, backend, record)
