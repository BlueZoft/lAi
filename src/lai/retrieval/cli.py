"""Operator-only retrieval evaluation. Emits aggregate metrics and fixed error codes."""

import argparse
import json
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from lai.corpus.cli import read_limited
from lai.corpus.graph import VersionGraph, document_nodes
from lai.corpus.models import SourceManifest
from lai.corpus.store import CorpusStore
from lai.retrieval.catalog import SourceCatalog
from lai.retrieval.embeddings import FakeEmbedding, load_local_bge
from lai.retrieval.engine import Retriever, index_document, index_selected_records
from lai.retrieval.evaluation import EvaluationDataset, evaluate
from lai.retrieval.index import MemoryIndex, RetrievalIndex
from lai.retrieval.models import RetrievalPolicy
from lai.retrieval.postgres import PostgresIndex, connect_local, migrate


class SyntheticTransliterator:
    """One invented-fixture lookup used exclusively by the synthetic demonstration."""

    def transliterate(self, text: str) -> str | None:
        return {"porma": "පෝරම"}.get(text)


def run_demo(args: argparse.Namespace) -> dict[str, object]:
    fixtures = Path("tests/fixtures")
    manifest = SourceManifest.model_validate_json(
        read_limited(fixtures / "synthetic-act.manifest.json")
    )
    raw = read_limited(fixtures / "synthetic-act.txt")
    dataset = EvaluationDataset.model_validate_json(
        read_limited(fixtures / "retrieval-queries.json")
    )
    backend = FakeEmbedding(
        aliases={"form": "forms", "පෝරම": "forms", "படிவம்": "forms", "porma": "forms"}
    )
    connection = None
    collection = "synthetic-demo-" + uuid4().hex
    try:
        if args.postgres:
            connection = connect_local(args.password_file)
            migrate(connection)
            index: RetrievalIndex = PostgresIndex(connection, collection, backend.identity)
        else:
            index = MemoryIndex(backend.identity)
        with tempfile.TemporaryDirectory(prefix="lai-synthetic-retrieval-") as directory:
            store = CorpusStore(Path(directory))
            record = store.ingest(manifest, raw, raw)
            catalog = SourceCatalog(store, VersionGraph(nodes=document_nodes(record)))
            index_document(catalog, index, backend, record.record_id, args.as_of)
            retriever = Retriever(
                catalog,
                index,
                backend,
                RetrievalPolicy(enabled=True, minimum_dense_similarity=0.05),
                SyntheticTransliterator(),
            )
            return evaluate(retriever, dataset, args.as_of)
    finally:
        if connection is not None:
            connection.execute(
                "DELETE FROM lai_retrieval.collections WHERE name = %s", (collection,)
            )
            connection.close()


def run_local_evaluation(args: argparse.Namespace) -> dict[str, object]:
    dataset = EvaluationDataset.model_validate_json(read_limited(args.dataset))
    graph = VersionGraph.model_validate_json(read_limited(args.graph))
    backend = load_local_bge(args.model_path, args.revision, args.device)
    catalog = SourceCatalog(CorpusStore(args.store), graph)
    index = MemoryIndex(backend.identity)
    index_selected_records(catalog, index, backend, args.record_id, args.as_of)
    retriever = Retriever(
        catalog,
        index,
        backend,
        RetrievalPolicy(
            enabled=True,
            source_scope="synthetic" if dataset.kind == "synthetic" else "real",
            minimum_dense_similarity=args.minimum_similarity,
        ),
    )
    return evaluate(retriever, dataset, args.as_of)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lai-retrieval")
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=datetime.now(ZoneInfo("Asia/Colombo")).date(),
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Evaluate only tiny synthetic sources with the fake backend"
    )
    demo.add_argument("--postgres", action="store_true")
    demo.add_argument("--password-file", type=Path, default=Path(".local/postgres.password"))
    local = commands.add_parser(
        "evaluate-local", help="Measure an existing local model and curated source set"
    )
    local.add_argument("--store", type=Path, required=True)
    local.add_argument("--graph", type=Path, required=True)
    local.add_argument("--dataset", type=Path, required=True)
    local.add_argument("--record-id", action="append", required=True)
    local.add_argument("--model-path", type=Path, required=True)
    local.add_argument("--revision", required=True)
    local.add_argument("--device", default="cpu")
    local.add_argument("--minimum-similarity", type=float, default=0.5)
    args = parser.parse_args(argv)
    try:
        report = run_demo(args) if args.command == "demo" else run_local_evaluation(args)
    except Exception:
        print(json.dumps({"error": "retrieval_operation_failed"}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
