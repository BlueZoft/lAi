from datetime import date

import pytest
from pydantic import ValidationError

from lai.corpus.graph import (
    EvidenceAnchor,
    VersionEdge,
    VersionGraph,
    VersionNode,
    document_nodes,
    verify_graph_evidence,
)
from lai.corpus.ingest import ingest_document
from lai.corpus.models import IngestionRecord, SourceManifest, digest


@pytest.fixture
def revision(source_manifest: SourceManifest, source_bytes: bytes) -> tuple[IngestionRecord, str]:
    text = source_bytes.replace(b"invented catalogue", b"revised synthetic catalogue")
    manifest = source_manifest.model_copy(
        update={
            "expected_raw_sha256": digest(text),
            "expected_text_sha256": digest(text),
        }
    )
    return ingest_document(manifest, text, text), text.decode()


def relationship(source: VersionNode, target: VersionNode, **changes: object) -> VersionEdge:
    edge = VersionEdge(
        relation="supersedes",
        source_node=source.id,
        target_node=target.id,
        evidence=EvidenceAnchor(
            record_id=source.record_id,
            start=source.start,
            end=source.end,
            text_sha256=source.text_sha256,
        ),
        effective_on=date(2099, 1, 1),
        reviewed=True,
    )
    return edge.model_copy(update=changes)


def test_empty_relationships_leave_status_unknown(
    ingested_record: IngestionRecord,
    source_bytes: bytes,
) -> None:
    graph = VersionGraph(nodes=document_nodes(ingested_record))
    result = graph.status(
        graph.nodes[1].id,
        date(2099, 2, 1),
        records=[ingested_record],
        texts={ingested_record.record_id: source_bytes.decode()},
    )
    assert result.amendment_status == result.commencement_status == "unknown"
    assert result.warnings == ("coverage_unverified",)


@pytest.mark.parametrize("relation", ["amends", "repeals", "commences", "supersedes"])
def test_reviewed_dated_relationships_are_scoped_and_anchored(
    ingested_record: IngestionRecord,
    source_bytes: bytes,
    revision: tuple[IngestionRecord, str],
    relation: str,
) -> None:
    changed, changed_text = revision
    before, after = document_nodes(ingested_record), document_nodes(changed)
    edge = relationship(after[1], before[1], relation=relation)
    graph = VersionGraph(nodes=before + after, edges=(edge,))
    records = [ingested_record, changed]
    texts = {ingested_record.record_id: source_bytes.decode(), changed.record_id: changed_text}
    verify_graph_evidence(graph, records, texts)
    result = graph.status(before[1].id, date(2099, 2, 1), records=records, texts=texts)
    assert (result.amendment_status == "amendment_recorded") == (relation == "amends")
    assert (result.amendment_status == "repeal_recorded") == (relation == "repeals")
    assert (result.commencement_status == "commencement_recorded") == (relation == "commences")
    assert result.replacement_recorded == (relation == "supersedes")
    unaffected = graph.status(before[2].id, date(2099, 2, 1), records=records, texts=texts)
    assert unaffected.amendment_status == unaffected.commencement_status == "unknown"


@pytest.mark.safety
@pytest.mark.parametrize(
    ("changes", "warning"),
    [
        ({"reviewed": False}, "unreviewed_relation"),
        ({"effective_on": None}, "effective_date_unknown"),
        ({"effective_on": date(2100, 1, 1)}, "future_effect_not_applied"),
    ],
)
def test_unreviewed_undated_or_future_edges_do_not_imply_status(
    ingested_record: IngestionRecord,
    source_bytes: bytes,
    revision: tuple[IngestionRecord, str],
    changes: dict[str, object],
    warning: str,
) -> None:
    changed, changed_text = revision
    before, after = document_nodes(ingested_record), document_nodes(changed)
    edge = relationship(after[1], before[1], relation="commences", **changes)
    graph = VersionGraph(nodes=before + after, edges=(edge,))
    result = graph.status(
        before[1].id,
        date(2099, 2, 1),
        records=[ingested_record, changed],
        texts={ingested_record.record_id: source_bytes.decode(), changed.record_id: changed_text},
    )
    assert result.commencement_status == "unknown"
    assert warning in result.warnings


def test_cycles_dangling_nodes_and_wrong_section_versions_are_rejected(
    ingested_record: IngestionRecord,
    revision: tuple[IngestionRecord, str],
) -> None:
    changed, _ = revision
    before, after = document_nodes(ingested_record), document_nodes(changed)
    edge = relationship(after[1], before[1])
    with pytest.raises(ValidationError, match="version_cycle"):
        VersionGraph(nodes=before + after, edges=(edge, relationship(before[1], after[1])))
    with pytest.raises(ValidationError, match="dangling_graph_edge"):
        VersionGraph(nodes=after, edges=(edge,))
    with pytest.raises(ValidationError, match="cross_provision_supersession"):
        VersionGraph(nodes=before + after, edges=(relationship(after[1], before[2]),))
    with pytest.raises(ValidationError, match="duplicate_graph_node"):
        VersionGraph(nodes=before + before)


@pytest.mark.safety
def test_status_checks_evidence_before_using_review_flags(
    ingested_record: IngestionRecord,
    source_bytes: bytes,
    revision: tuple[IngestionRecord, str],
) -> None:
    changed, changed_text = revision
    before, after = document_nodes(ingested_record), document_nodes(changed)
    bad_anchor = EvidenceAnchor(
        record_id=changed.record_id, start=after[1].start, end=after[1].end, text_sha256="0" * 64
    )
    edge = relationship(after[1], before[1], evidence=bad_anchor)
    graph = VersionGraph(nodes=before + after, edges=(edge,))
    with pytest.raises(ValueError, match="graph_evidence_hash_mismatch"):
        graph.status(
            before[1].id,
            date(2099, 2, 1),
            records=[ingested_record, changed],
            texts={
                ingested_record.record_id: source_bytes.decode(),
                changed.record_id: changed_text,
            },
        )


@pytest.mark.safety
def test_bad_extraction_cannot_support_a_reviewed_relationship(
    source_manifest: SourceManifest,
    source_bytes: bytes,
    ingested_record: IngestionRecord,
) -> None:
    extraction = source_manifest.extraction.model_copy(update={"fonts": ("FM Abhaya",)})
    text = source_bytes + b"\nSYNTHETIC additional source material.\n"
    bad = ingest_document(
        source_manifest.model_copy(
            update={
                "extraction": extraction,
                "expected_raw_sha256": digest(text),
                "expected_text_sha256": digest(text),
            }
        ),
        text,
        text,
    )
    before, after = document_nodes(ingested_record), document_nodes(bad)
    graph = VersionGraph(nodes=before + after, edges=(relationship(after[1], before[1]),))
    with pytest.raises(ValueError, match="reviewed_edge_requires_reviewed_readable_source"):
        verify_graph_evidence(
            graph,
            [ingested_record, bad],
            {
                ingested_record.record_id: source_bytes.decode(),
                bad.record_id: text.decode(),
            },
        )


def test_mirror_observation_does_not_create_a_new_content_version(
    ingested_record: IngestionRecord,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    source = source_manifest.source.model_copy(
        update={
            "url": "https://mirror.example.invalid/synthetic-act",
            "role": "mirror",
        }
    )
    mirror = ingest_document(
        source_manifest.model_copy(update={"source": source}), source_bytes, source_bytes
    )
    assert mirror.record_id != ingested_record.record_id
    assert [node.id for node in document_nodes(mirror)] == [
        node.id for node in document_nodes(ingested_record)
    ]
