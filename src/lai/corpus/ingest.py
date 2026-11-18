"""Pure ingestion pipeline and explicit canonical-source selection."""

from collections.abc import Sequence

from lai.corpus.models import IngestionRecord, SourceManifest, content_id, digest
from lai.corpus.parser import parse_act
from lai.corpus.quality import assess_text

MAX_DOCUMENT_BYTES = 32 * 1024 * 1024


def ingest_document(manifest: SourceManifest, raw: bytes, text_bytes: bytes) -> IngestionRecord:
    if max(len(raw), len(text_bytes)) > MAX_DOCUMENT_BYTES:
        raise ValueError("document_size_limit")
    if digest(raw) != manifest.expected_raw_sha256:
        raise ValueError("raw_hash_mismatch")
    if digest(text_bytes) != manifest.expected_text_sha256:
        raise ValueError("text_hash_mismatch")
    text = text_bytes.decode("utf-8", errors="strict")
    quality = assess_text(text, manifest.language, manifest.extraction)
    parsed = parse_act(text, manifest.language, manifest.instrument)
    payload = {
        "schema_version": "1",
        "manifest": manifest.model_dump(mode="json"),
        "quality": quality.model_dump(mode="json"),
        "parsed": parsed.model_dump(mode="json"),
    }
    return IngestionRecord(
        record_id=content_id(payload), manifest=manifest, quality=quality, parsed=parsed
    )


def select_canonical(records: Sequence[IngestionRecord]) -> IngestionRecord:
    """Select among equivalent content, preserving every observation in storage."""
    if not records:
        raise ValueError("no_source_candidates")
    identities = {
        (
            record.manifest.expected_raw_sha256,
            record.manifest.expected_text_sha256,
            record.manifest.language,
            record.manifest.instrument,
        )
        for record in records
    }
    if len(identities) != 1:
        raise ValueError("conflicting_document_identity")
    roles = {"official": 0, "mirror": 1, "manual": 2}
    return min(
        records,
        key=lambda record: (
            not record.eligible_for_retrieval,
            not record.manifest.source.metadata_reviewed,
            roles[record.manifest.source.role],
            -record.manifest.source.fetched_at.timestamp(),
            record.manifest.source.url,
            record.record_id,
        ),
    )
