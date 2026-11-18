"""Resolve index references against preserved source bytes and scoped graph evidence."""

from datetime import date

from lai.corpus.graph import VersionGraph, document_nodes
from lai.corpus.models import IngestionRecord, content_id
from lai.corpus.store import CorpusStore
from lai.retrieval.models import Citation, SectionChunk


def document_key(record: IngestionRecord) -> str:
    return content_id(
        {"instrument": record.manifest.instrument.id, "language": record.manifest.language}
    )


def record_chunks(record: IngestionRecord) -> tuple[SectionChunk, ...]:
    nodes = {node.section_number: node for node in document_nodes(record)}
    return tuple(
        SectionChunk(
            id=nodes[section.number].id,
            document_key=document_key(record),
            record_id=record.record_id,
            section_number=section.number,
            start=section.start,
            end=section.end,
            text=section.text,
            text_sha256=section.text_sha256,
            language=record.manifest.language,
            instrument_id=record.manifest.instrument.id,
            synthetic=record.manifest.instrument.synthetic,
        )
        for section in record.parsed.sections
    )


class SourceCatalog:
    def __init__(self, store: CorpusStore, graph: VersionGraph):
        self.store = store
        self.graph = graph
        self.nodes = {node.id: node for node in graph.nodes}

    def resolve(self, chunk: SectionChunk, as_of: date, warning_days: int = 90) -> Citation:
        record = self.store.load(chunk.record_id)
        if not record.eligible_for_retrieval:
            raise ValueError("source_quarantined")
        expected = next((item for item in record_chunks(record) if item.id == chunk.id), None)
        if expected != chunk:
            raise ValueError("citation_anchor_invalid")
        document = document_nodes(record)[0]
        targets = {document.id, chunk.id}
        edges = tuple(edge for edge in self.graph.edges if edge.target_node in targets)
        required = targets | {edge.source_node for edge in edges}
        if not required <= self.nodes.keys():
            raise ValueError("version_evidence_missing")
        graph = VersionGraph(nodes=tuple(self.nodes[key] for key in sorted(required)), edges=edges)
        ids = sorted({node.record_id for node in graph.nodes} | {record.record_id})
        records = [self.store.load(key) for key in ids]
        texts = {
            item.record_id: (self.store.root / "text" / item.manifest.expected_text_sha256)
            .read_bytes()
            .decode("utf-8")
            for item in records
        }
        statuses = [
            graph.status(key, as_of, records=records, texts=texts) for key in sorted(targets)
        ]
        if any(
            item.amendment_status != "unknown" or item.replacement_recorded for item in statuses
        ):
            raise ValueError("version_requires_review")
        warnings = {warning for status in statuses for warning in status.warnings}
        warnings.add("legal_currency_unverified")
        if (as_of - record.manifest.source.fetched_at.date()).days > warning_days:
            warnings.add("source_acquisition_age_warning")
        if record.manifest.source.fetched_at.date() > as_of:
            warnings.add("source_acquired_after_asof")
        manifest = record.manifest
        if manifest.instrument.number is None or manifest.instrument.year is None:
            raise ValueError("instrument_identity_incomplete")
        return Citation(
            record_id=record.record_id,
            instrument_type=manifest.instrument.kind,
            instrument_id=manifest.instrument.id,
            number=manifest.instrument.number,
            year=manifest.instrument.year,
            section=chunk.section_number,
            language=manifest.language,
            source_url=manifest.source.url,
            canonical_url=manifest.source.canonical_url,
            retrieved_at=manifest.source.fetched_at,
            source_revision=manifest.source.revision,
            raw_sha256=manifest.expected_raw_sha256,
            text_sha256=manifest.expected_text_sha256,
            section_sha256=chunk.text_sha256,
            start=chunk.start,
            end=chunk.end,
            amendment_status="unknown",
            commencement_status=(
                "commencement_recorded"
                if any(status.commencement_status == "commencement_recorded" for status in statuses)
                else "unknown"
            ),
            staleness_warnings=tuple(sorted(warnings)),
        )

    def eligible_chunks(
        self, record_id: str, as_of: date
    ) -> tuple[IngestionRecord, tuple[SectionChunk, ...]]:
        record = self.store.load(record_id)
        if not record.eligible_for_retrieval:
            return record, ()
        chunks: list[SectionChunk] = []
        for chunk in record_chunks(record):
            try:
                self.resolve(chunk, as_of)
            except ValueError:
                continue
            chunks.append(chunk)
        return record, tuple(chunks)
