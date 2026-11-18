"""Evidence-backed version relationships with explicit unknown legal status."""

from collections import deque
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from lai.corpus.models import (
    Contract,
    Identifier,
    IngestionRecord,
    Language,
    Sha256,
    content_id,
    digest,
)


class VersionNode(Contract):
    id: Sha256
    record_id: Sha256
    raw_sha256: Sha256
    extracted_text_sha256: Sha256
    instrument_id: Identifier
    language: Language
    section_number: str | None
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text_sha256: Sha256

    @model_validator(mode="after")
    def check_identity(self) -> Self:
        if (
            self.start >= self.end
            or content_id(self.model_dump(mode="json", exclude={"id", "record_id"})) != self.id
        ):
            raise ValueError("version_node_invalid")
        return self


class EvidenceAnchor(Contract):
    record_id: Sha256
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text_sha256: Sha256

    @model_validator(mode="after")
    def check_span(self) -> Self:
        if self.end <= self.start:
            raise ValueError("evidence_span_invalid")
        return self


class VersionEdge(Contract):
    relation: Literal["amends", "repeals", "commences", "supersedes"]
    source_node: Sha256
    target_node: Sha256
    evidence: EvidenceAnchor
    effective_on: date | None = None
    reviewed: bool = False


class VersionStatus(Contract):
    amendment_status: Literal["unknown", "amendment_recorded", "repeal_recorded"] = "unknown"
    commencement_status: Literal["unknown", "commencement_recorded"] = "unknown"
    replacement_recorded: bool = False
    warnings: tuple[str, ...]


class VersionGraph(Contract):
    schema_version: Literal["1"] = "1"
    nodes: tuple[VersionNode, ...] = ()
    edges: tuple[VersionEdge, ...] = ()

    @model_validator(mode="after")
    def check_structure(self) -> Self:
        nodes = {node.id: node for node in self.nodes}
        if len(nodes) != len(self.nodes):
            raise ValueError("duplicate_graph_node")
        if len(set(self.edges)) != len(self.edges):
            raise ValueError("duplicate_graph_edge")
        successors: dict[str, set[str]] = {key: set() for key in nodes}
        indegrees = dict.fromkeys(nodes, 0)
        for edge in self.edges:
            if edge.source_node not in nodes or edge.target_node not in nodes:
                raise ValueError("dangling_graph_edge")
            if edge.source_node == edge.target_node:
                raise ValueError("self_graph_edge")
            source, target = nodes[edge.source_node], nodes[edge.target_node]
            if edge.evidence.record_id != source.record_id:
                raise ValueError("evidence_source_mismatch")
            if edge.evidence.start < source.start or edge.evidence.end > source.end:
                raise ValueError("evidence_outside_source_node")
            if edge.relation == "supersedes":
                source_identity = (source.instrument_id, source.language, source.section_number)
                target_identity = (target.instrument_id, target.language, target.section_number)
                if source_identity != target_identity:
                    raise ValueError("cross_provision_supersession")
                if target.id not in successors[source.id]:
                    successors[source.id].add(target.id)
                    indegrees[target.id] += 1
        pending = deque(key for key, degree in indegrees.items() if degree == 0)
        visited = 0
        while pending:
            node_id = pending.popleft()
            visited += 1
            for successor in successors[node_id]:
                indegrees[successor] -= 1
                if indegrees[successor] == 0:
                    pending.append(successor)
        if visited != len(nodes):
            raise ValueError("version_cycle")
        return self

    def status(
        self,
        node_id: str,
        as_of: date,
        *,
        records: Sequence[IngestionRecord],
        texts: Mapping[str, str],
    ) -> VersionStatus:
        verify_graph_evidence(self, records, texts)
        if node_id not in {node.id for node in self.nodes}:
            raise ValueError("unknown_version_node")
        warnings = {"coverage_unverified"}
        observed: set[str] = set()
        for edge in self.edges:
            if edge.target_node != node_id:
                continue
            if not edge.reviewed:
                warnings.add("unreviewed_relation")
            elif edge.effective_on is None:
                warnings.add("effective_date_unknown")
            elif edge.effective_on > as_of:
                warnings.add("future_effect_not_applied")
            else:
                observed.add(edge.relation)
        amendment: Literal["unknown", "amendment_recorded", "repeal_recorded"] = "unknown"
        if "repeals" in observed:
            amendment = "repeal_recorded"
        elif "amends" in observed:
            amendment = "amendment_recorded"
        return VersionStatus(
            amendment_status=amendment,
            commencement_status="commencement_recorded" if "commences" in observed else "unknown",
            replacement_recorded="supersedes" in observed,
            warnings=tuple(sorted(warnings)),
        )


def document_nodes(record: IngestionRecord) -> tuple[VersionNode, ...]:
    manifest = record.manifest
    spans: list[tuple[str | None, int, int, str]] = [
        (None, 0, record.quality.character_count, manifest.expected_text_sha256)
    ]
    spans.extend(
        (section.number, section.start, section.end, section.text_sha256)
        for section in record.parsed.sections
    )
    nodes: list[VersionNode] = []
    for number, start, end, text_hash in spans:
        if end == 0:
            continue
        payload = {
            "raw_sha256": manifest.expected_raw_sha256,
            "extracted_text_sha256": manifest.expected_text_sha256,
            "instrument_id": manifest.instrument.id,
            "language": manifest.language,
            "section_number": number,
            "start": start,
            "end": end,
            "text_sha256": text_hash,
        }
        nodes.append(
            VersionNode.model_validate(
                payload | {"id": content_id(payload), "record_id": record.record_id}
            )
        )
    return tuple(nodes)


def verify_graph_evidence(
    graph: VersionGraph,
    records: Sequence[IngestionRecord],
    texts: Mapping[str, str],
) -> None:
    """Check graph anchors against hash-verified source records and extracted bytes."""
    available = {record.record_id: record for record in records}
    allowed_nodes = {
        (node.record_id, node.id): node for record in records for node in document_nodes(record)
    }
    if any(allowed_nodes.get((node.record_id, node.id)) != node for node in graph.nodes):
        raise ValueError("graph_node_source_missing")
    for record in records:
        text = texts.get(record.record_id)
        if text is None or digest(text.encode("utf-8")) != record.manifest.expected_text_sha256:
            raise ValueError("graph_source_text_mismatch")
    for edge in graph.edges:
        anchor = edge.evidence
        record = available[anchor.record_id]
        text = texts[anchor.record_id]
        if (
            anchor.end > len(text)
            or digest(text[anchor.start : anchor.end].encode("utf-8")) != anchor.text_sha256
        ):
            raise ValueError("graph_evidence_hash_mismatch")
        if edge.reviewed and (
            not record.quality.eligible or not record.manifest.source.metadata_reviewed
        ):
            raise ValueError("reviewed_edge_requires_reviewed_readable_source")
