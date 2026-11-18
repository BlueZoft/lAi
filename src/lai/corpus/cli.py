"""Operator intake commands. Responses contain codes, counts and hashes only."""

import argparse
import json
import sys
from pathlib import Path

from lai.corpus.graph import VersionGraph, document_nodes, verify_graph_evidence
from lai.corpus.ingest import MAX_DOCUMENT_BYTES
from lai.corpus.models import SourceManifest
from lai.corpus.store import CorpusStore, write_immutable


def read_limited(path: Path, limit: int = MAX_DOCUMENT_BYTES) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("input_size_limit")
    return data


def ingest(args: argparse.Namespace) -> None:
    manifest = SourceManifest.model_validate_json(read_limited(args.manifest, 1_000_000))
    store = CorpusStore(args.store)
    record = store.ingest(manifest, read_limited(args.raw), read_limited(args.text))
    graph = VersionGraph(nodes=document_nodes(record))
    write_immutable(
        args.store / "graphs" / f"{record.record_id}.json",
        (graph.model_dump_json(indent=2) + "\n").encode("utf-8"),
    )
    print(
        json.dumps(
            {
                "record_id": record.record_id,
                "quality_score": record.quality.score,
                "sections": len(record.parsed.sections),
                "eligible_for_retrieval": record.eligible_for_retrieval,
                "quarantine_reasons": record.quarantine_reasons,
            }
        )
    )


def graph_check(args: argparse.Namespace) -> None:
    graph = VersionGraph.model_validate_json(read_limited(args.graph, 1_000_000))
    store = CorpusStore(args.store)
    records = [store.load(key) for key in sorted({node.record_id for node in graph.nodes})]
    texts = {
        record.record_id: read_limited(
            store.root / "text" / record.manifest.expected_text_sha256
        ).decode("utf-8")
        for record in records
    }
    verify_graph_evidence(graph, records, texts)
    print(json.dumps({"graph_valid": True, "nodes": len(graph.nodes), "edges": len(graph.edges)}))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lai-corpus")
    commands = parser.add_subparsers(dest="command", required=True)
    intake = commands.add_parser(
        "ingest", help="Ingest an explicit manifest, raw artefact and UTF-8 text"
    )
    intake.add_argument("--manifest", type=Path, required=True)
    intake.add_argument("--raw", type=Path, required=True)
    intake.add_argument("--text", type=Path, required=True)
    intake.add_argument("--store", type=Path, default=Path("data/corpus"))
    check = commands.add_parser(
        "graph-check", help="Check graph evidence against staged source artefacts"
    )
    check.add_argument("--graph", type=Path, required=True)
    check.add_argument("--store", type=Path, default=Path("data/corpus"))
    args = parser.parse_args(argv)
    try:
        if args.command == "ingest":
            ingest(args)
        else:
            graph_check(args)
    except (OSError, ValueError):
        print(json.dumps({"error": "corpus_operation_failed"}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
