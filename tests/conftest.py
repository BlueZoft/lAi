from pathlib import Path

import pytest

from lai.corpus.ingest import ingest_document
from lai.corpus.models import IngestionRecord, SourceManifest

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
