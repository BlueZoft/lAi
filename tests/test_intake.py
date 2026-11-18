import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from pydantic import ValidationError

from lai.corpus.cli import main
from lai.corpus.ingest import ingest_document, select_canonical
from lai.corpus.models import IngestionRecord, SourceManifest, digest
from lai.corpus.store import CorpusStore


def test_manifest_requires_hashes_timezone_and_known_fields(
    source_manifest: SourceManifest,
) -> None:
    data = source_manifest.model_dump(mode="json")
    data["expected_raw_sha256"] = "invalid"
    with pytest.raises(ValidationError):
        SourceManifest.model_validate_json(json.dumps(data))
    data = source_manifest.model_dump(mode="json")
    data["source"]["fetched_at"] = "2026-11-18T00:00:00"
    with pytest.raises(ValidationError):
        SourceManifest.model_validate_json(json.dumps(data))
    data = source_manifest.model_dump(mode="json") | {"model_approved": True}
    with pytest.raises(ValidationError):
        SourceManifest.model_validate_json(json.dumps(data))


@pytest.mark.parametrize(
    "url",
    [
        "file:///synthetic",
        "https://user:secret@example.invalid/source",
        "https://example.invalid/source?token=SYNTHETIC",
        "https://example.invalid/source#fragment",
    ],
)
@pytest.mark.parametrize("field", ["url", "canonical_url"])
def test_manifest_rejects_nonpublic_source_urls(
    source_manifest: SourceManifest,
    url: str,
    field: str,
) -> None:
    data = source_manifest.model_dump(mode="json")
    data["source"][field] = url
    with pytest.raises(ValidationError):
        SourceManifest.model_validate_json(json.dumps(data))


def test_intake_keeps_verbatim_anchors_and_hashes(
    ingested_record: IngestionRecord,
    source_bytes: bytes,
) -> None:
    record = ingested_record
    assert record.eligible_for_retrieval
    assert [section.number for section in record.parsed.sections] == ["1", "2", "3"]
    for section in record.parsed.sections:
        assert section.text == source_bytes.decode()[section.start : section.end]
        assert section.text_sha256 == digest(section.text.encode())
    assert "PART II" not in record.parsed.sections[1].text
    assert (
        record.record_id == IngestionRecord.model_validate_json(record.model_dump_json()).record_id
    )


def test_hash_mismatch_has_no_store_side_effects(
    tmp_path: Path,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    store = CorpusStore(tmp_path / "store")
    with pytest.raises(ValueError, match="raw_hash_mismatch"):
        store.ingest(source_manifest, b"SYNTHETIC changed bytes", source_bytes)
    assert not store.root.exists()
    with pytest.raises(ValueError, match="text_hash_mismatch"):
        store.ingest(source_manifest, source_bytes, b"SYNTHETIC changed extraction")
    assert not store.root.exists()


def test_non_utf8_is_rejected_before_storage(
    tmp_path: Path, source_manifest: SourceManifest
) -> None:
    data = b"\xff\xfeSYNTHETIC"
    manifest = source_manifest.model_copy(
        update={
            "expected_raw_sha256": digest(data),
            "expected_text_sha256": digest(data),
        }
    )
    store = CorpusStore(tmp_path / "store")
    with pytest.raises(UnicodeDecodeError):
        store.ingest(manifest, data, data)
    assert not store.root.exists()


def test_repeated_and_concurrent_intake_is_idempotent(
    tmp_path: Path,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    store = CorpusStore(tmp_path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(
            pool.map(lambda _: store.ingest(source_manifest, source_bytes, source_bytes), range(8))
        )
    assert len({record.record_id for record in records}) == 1
    assert len(list((tmp_path / "raw").iterdir())) == 1
    assert len(list((tmp_path / "text").iterdir())) == 1
    assert len(list((tmp_path / "records").iterdir())) == 1
    assert store.load(records[0].record_id) == records[0]


def test_retry_after_record_commit_failure(
    tmp_path: Path,
    source_manifest: SourceManifest,
    source_bytes: bytes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import lai.corpus.store as storage

    original = storage.write_immutable

    def fail_record(path: Path, data: bytes) -> None:
        if path.parent.name == "records":
            raise OSError("SYNTHETIC interruption")
        original(path, data)

    store = CorpusStore(tmp_path)
    with monkeypatch.context() as context:
        context.setattr(storage, "write_immutable", fail_record)
        with pytest.raises(OSError):
            store.ingest(source_manifest, source_bytes, source_bytes)
    assert not list((tmp_path / "records").glob("*.json"))
    record = store.ingest(source_manifest, source_bytes, source_bytes)
    assert store.load(record.record_id) == record


def test_store_revalidates_corrupted_extraction(
    tmp_path: Path,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    store = CorpusStore(tmp_path)
    record = store.ingest(source_manifest, source_bytes, source_bytes)
    (tmp_path / "text" / source_manifest.expected_text_sha256).write_bytes(b"SYNTHETIC corruption")
    with pytest.raises(ValueError, match="text_hash_mismatch"):
        store.load(record.record_id)


def test_dedupe_keeps_observations_and_selects_reviewed_official_source(
    tmp_path: Path,
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    store = CorpusStore(tmp_path)
    official = store.ingest(source_manifest, source_bytes, source_bytes)
    mirror_source = source_manifest.source.model_copy(
        update={
            "url": "https://mirror.example.invalid/synthetic-act",
            "role": "mirror",
        }
    )
    mirror = store.ingest(
        source_manifest.model_copy(update={"source": mirror_source}), source_bytes, source_bytes
    )
    assert official.record_id != mirror.record_id
    assert len(list((tmp_path / "raw").iterdir())) == 1
    assert len(list((tmp_path / "records").iterdir())) == 2
    assert select_canonical([mirror, official]) == official
    assert select_canonical([official, mirror]) == official
    conflicting = source_manifest.instrument.model_copy(update={"id": "synthetic-other-instrument"})
    other = ingest_document(
        source_manifest.model_copy(update={"instrument": conflicting}), source_bytes, source_bytes
    )
    with pytest.raises(ValueError, match="conflicting_document_identity"):
        select_canonical([official, other])


@pytest.mark.safety
def test_unreviewed_or_incomplete_source_stays_quarantined(
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    unreviewed = source_manifest.source.model_copy(update={"metadata_reviewed": False})
    record = ingest_document(
        source_manifest.model_copy(update={"source": unreviewed}), source_bytes, source_bytes
    )
    assert not record.eligible_for_retrieval
    assert "source_unreviewed" in record.quarantine_reasons
    unknown = source_manifest.instrument.model_copy(update={"number": None})
    record = ingest_document(
        source_manifest.model_copy(update={"instrument": unknown}), source_bytes, source_bytes
    )
    assert "instrument_identity_incomplete" in record.quarantine_reasons


def test_manual_seed_requires_gap_mapping_and_preserves_it(
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    data = source_manifest.model_dump(mode="json") | {"acquisition": "manual_seed"}
    with pytest.raises(ValidationError, match="manual_seed_requires_gap_ids"):
        SourceManifest.model_validate_json(json.dumps(data))
    data["gap_ids"] = ["synthetic-foundational-gap"]
    data["instrument"]["year"] = 1900
    record = ingest_document(
        SourceManifest.model_validate_json(json.dumps(data)), source_bytes, source_bytes
    )
    assert record.manifest.gap_ids == ("synthetic-foundational-gap",)
    assert record.manifest.acquisition == "manual_seed"


def test_cli_normal_entry_point_and_error_redaction(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = Path(__file__).parent / "fixtures"
    args = [
        "ingest",
        "--manifest",
        str(fixture / "synthetic-act.manifest.json"),
        "--raw",
        str(fixture / "synthetic-act.txt"),
        "--text",
        str(fixture / "synthetic-act.txt"),
        "--store",
        str(tmp_path),
    ]
    assert main(args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["eligible_for_retrieval"] is True
    assert result["sections"] == 3
    graph = tmp_path / "graphs" / f"{result['record_id']}.json"
    assert main(["graph-check", "--graph", str(graph), "--store", str(tmp_path)]) == 0
    assert json.loads(capsys.readouterr().out)["graph_valid"] is True
    bad = tmp_path / "manifest.json"
    bad.write_text('{"SYNTHETIC_SENSITIVE_SENTINEL": "invalid"}')
    args[2] = str(bad)
    assert main(args) == 2
    captured = capsys.readouterr()
    assert json.loads(captured.err) == {"error": "corpus_operation_failed"}
    assert "SYNTHETIC_SENSITIVE_SENTINEL" not in captured.err + captured.out
