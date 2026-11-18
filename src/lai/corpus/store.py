"""Immutable staging artefacts, committed last through a content-addressed record."""

import os
import tempfile
from pathlib import Path

from lai.corpus.ingest import ingest_document
from lai.corpus.models import IngestionRecord, SourceManifest, digest


def write_immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.is_symlink() or digest(path.read_bytes()) != digest(data):
                raise ValueError("stored_artifact_conflict") from None
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class CorpusStore:
    def __init__(self, root: Path):
        self.root = root

    def ingest(self, manifest: SourceManifest, raw: bytes, text: bytes) -> IngestionRecord:
        record = ingest_document(manifest, raw, text)
        write_immutable(self.root / "raw" / manifest.expected_raw_sha256, raw)
        write_immutable(self.root / "text" / manifest.expected_text_sha256, text)
        record_bytes = (record.model_dump_json(indent=2) + "\n").encode("utf-8")
        write_immutable(self.root / "records" / f"{record.record_id}.json", record_bytes)
        return record

    def load(self, record_id: str) -> IngestionRecord:
        if len(record_id) != 64 or any(
            character not in "0123456789abcdef" for character in record_id
        ):
            raise ValueError("record_id_invalid")
        record = IngestionRecord.model_validate_json(
            (self.root / "records" / f"{record_id}.json").read_bytes()
        )
        if record.record_id != record_id:
            raise ValueError("record_id_mismatch")
        manifest = record.manifest
        rebuilt = ingest_document(
            manifest,
            (self.root / "raw" / manifest.expected_raw_sha256).read_bytes(),
            (self.root / "text" / manifest.expected_text_sha256).read_bytes(),
        )
        if rebuilt != record:
            raise ValueError("record_revalidation_failed")
        return record
