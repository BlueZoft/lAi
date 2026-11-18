from datetime import UTC, date, datetime

import pytest
from conftest import RetrievalContext

from lai.corpus.graph import EvidenceAnchor, VersionEdge, VersionGraph, document_nodes
from lai.corpus.models import SourceManifest
from lai.retrieval.catalog import SourceCatalog, record_chunks
from lai.retrieval.engine import Retriever, index_document, index_selected_records
from lai.retrieval.models import EncodedSection, RetrievalPolicy

AS_OF = date(2026, 11, 18)


@pytest.mark.safety
@pytest.mark.parametrize("relation", ["amends", "repeals", "supersedes"])
def test_document_level_stale_version_blocks_all_sections(
    retrieval_context: RetrievalContext,
    source_bytes: bytes,
    source_manifest: SourceManifest,
    relation: str,
) -> None:
    from lai.corpus.models import digest

    context = retrieval_context
    changed = source_bytes + b"\nSYNTHETIC second source version.\n"
    manifest = source_manifest.model_copy(
        update={
            "expected_raw_sha256": digest(changed),
            "expected_text_sha256": digest(changed),
        }
    )
    newer = context.catalog.store.ingest(manifest, changed, changed)
    before, after = document_nodes(context.record), document_nodes(newer)
    edge = VersionEdge.model_validate(
        {
            "relation": relation,
            "source_node": after[0].id,
            "target_node": before[0].id,
            "evidence": EvidenceAnchor(
                record_id=newer.record_id,
                start=after[0].start,
                end=after[0].end,
                text_sha256=after[0].text_sha256,
            ),
            "reviewed": True,
            "effective_on": date(2026, 1, 1),
        }
    )
    catalog = SourceCatalog(
        context.catalog.store, VersionGraph(nodes=before + after, edges=(edge,))
    )
    engine = Retriever(
        catalog,
        context.index,
        context.backend,
        RetrievalPolicy(enabled=True, minimum_dense_similarity=0.05),
    )
    result = engine.retrieve("catalogue", AS_OF)
    assert result.status == "abstained" and not result.candidates


def test_unreviewed_source_reindex_removes_old_active_sections(
    retrieval_context: RetrievalContext,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    context = retrieval_context
    source = source_manifest.source.model_copy(update={"metadata_reviewed": False})
    record = context.catalog.store.ingest(
        source_manifest.model_copy(update={"source": source}), source_bytes, source_bytes
    )
    count = index_document(context.catalog, context.index, context.backend, record.record_id, AS_OF)
    assert count == 0
    assert len(context.index.search(context.backend.embed(["catalogue"])[0]).dense) == 0
    assert len(context.index.records) == 2


def test_failed_embedding_update_leaves_previous_document_unchanged(
    retrieval_context: RetrievalContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = retrieval_context
    before = context.index.documents.copy()

    def broken(texts: object) -> None:
        raise RuntimeError("SYNTHETIC model unavailable")

    monkeypatch.setattr(context.backend, "embed", broken)
    with pytest.raises(RuntimeError):
        index_document(
            context.catalog, context.index, context.backend, context.record.record_id, AS_OF
        )
    assert context.index.documents == before


def test_source_acquisition_age_is_a_warning_without_inventing_legal_dates(
    retrieval_context: RetrievalContext,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    source = source_manifest.source.model_copy(
        update={"fetched_at": datetime(2020, 1, 1, tzinfo=UTC)}
    )
    record = retrieval_context.catalog.store.ingest(
        source_manifest.model_copy(update={"source": source}), source_bytes, source_bytes
    )
    catalog = SourceCatalog(
        retrieval_context.catalog.store, VersionGraph(nodes=document_nodes(record))
    )
    citation = catalog.resolve(record_chunks(record)[0], AS_OF)
    assert "source_acquisition_age_warning" in citation.staleness_warnings
    assert citation.amendment_status == citation.commencement_status == "unknown"


def test_index_rejects_chunk_record_or_dimension_mismatch(
    retrieval_context: RetrievalContext,
) -> None:
    context = retrieval_context
    chunk = record_chunks(context.record)[0]
    vector = context.backend.embed([chunk.text])[0]
    bad = chunk.model_copy(update={"document_key": "0" * 64})
    with pytest.raises(ValueError, match="indexed_chunk_source_mismatch"):
        context.index.replace_document(context.record, [EncodedSection(chunk=bad, vector=vector)])


def test_equivalent_acquisitions_do_not_duplicate_provisions(
    retrieval_context: RetrievalContext,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    context = retrieval_context
    source = source_manifest.source.model_copy(
        update={"url": "https://mirror.example.invalid/synthetic", "role": "mirror"}
    )
    mirror = context.catalog.store.ingest(
        source_manifest.model_copy(update={"source": source}), source_bytes, source_bytes
    )
    catalog = SourceCatalog(context.catalog.store, VersionGraph(nodes=document_nodes(mirror)))
    index_document(catalog, context.index, context.backend, mirror.record_id, AS_OF)
    result = Retriever(
        catalog,
        context.index,
        context.backend,
        RetrievalPolicy(enabled=True, minimum_dense_similarity=0.05),
    ).retrieve("catalogue", AS_OF)
    assert len(result.candidates) == 3
    assert len({item.citation.section for item in result.candidates}) == 3


def test_batch_selection_rejects_ambiguous_versions_before_updates(
    retrieval_context: RetrievalContext,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    from lai.corpus.models import digest

    context = retrieval_context
    changed = source_bytes + b"\nSYNTHETIC distinct version.\n"
    manifest = source_manifest.model_copy(
        update={
            "expected_raw_sha256": digest(changed),
            "expected_text_sha256": digest(changed),
        }
    )
    version = context.catalog.store.ingest(manifest, changed, changed)
    before = context.index.documents.copy()
    with pytest.raises(ValueError, match="conflicting_document_identity"):
        index_selected_records(
            context.catalog,
            context.index,
            context.backend,
            [context.record.record_id, version.record_id],
            AS_OF,
        )
    assert context.index.documents == before
