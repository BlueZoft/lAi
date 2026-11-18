import pytest

from lai.corpus.ingest import ingest_document
from lai.corpus.models import SourceManifest, digest
from lai.corpus.quality import assess_text


@pytest.mark.safety
@pytest.mark.parametrize(
    ("suffix", "issue"),
    [
        ("\ufffd", "replacement_character"),
        ("\ue001", "private_use_glyphs"),
        ("\x00", "control_characters"),
        ("\u00e0\u00b6", "mojibake"),
        ("Z" * 20, "repeated_glyphs"),
    ],
)
def test_garbled_extraction_is_quarantined(
    source_manifest: SourceManifest,
    source_bytes: bytes,
    suffix: str,
    issue: str,
) -> None:
    text = source_bytes + suffix.encode()
    manifest = source_manifest.model_copy(update={"expected_text_sha256": digest(text)})
    record = ingest_document(manifest, source_bytes, text)
    assert issue in record.quarantine_reasons
    assert not record.eligible_for_retrieval
    assert record.quality.score < 0.8


@pytest.mark.safety
@pytest.mark.parametrize("font", ["FM Abhaya", "ABCDEF+FMAbhaya", "DL-Manel", "dl manel"])
def test_legacy_fonts_are_quarantined(
    source_manifest: SourceManifest,
    source_bytes: bytes,
    font: str,
) -> None:
    extraction = source_manifest.extraction.model_copy(update={"fonts": (font,)})
    manifest = source_manifest.model_copy(update={"extraction": extraction})
    record = ingest_document(manifest, source_bytes, source_bytes)
    assert "legacy_font" in record.quarantine_reasons
    assert not record.eligible_for_retrieval


@pytest.mark.parametrize("text", ["", "    \n", "SYNTHETIC", "!" * 100])
def test_empty_or_unusable_text_is_not_eligible(source_manifest: SourceManifest, text: str) -> None:
    result = assess_text(text, "en", source_manifest.extraction)
    assert not result.eligible
    assert result.issues


def test_declared_script_mismatch_is_quarantined(
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    result = assess_text(source_bytes.decode(), "si", source_manifest.extraction)
    assert result.declared_script_ratio == 0
    assert "declared_script_mismatch" in result.issues


def test_synthetic_dividers_do_not_trigger_repeated_letter_detection(
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    result = assess_text(source_bytes.decode() + "\n" + "_" * 60, "en", source_manifest.extraction)
    assert result.eligible


def test_combining_marks_do_not_reduce_readability(source_manifest: SourceManifest) -> None:
    result = assess_text(" ".join(["தமிழ்"] * 40), "ta", source_manifest.extraction)
    assert result.alphabetic_ratio == 1.0
    assert result.eligible


@pytest.mark.parametrize(("language", "word"), [("si", "සිංහල"), ("ta", "தமிழ்")])
def test_unicode_language_text_can_pass_quality_without_claiming_parser_support(
    source_manifest: SourceManifest,
    language: str,
    word: str,
) -> None:
    text = (" ".join([word] * 40)).encode()
    data = source_manifest.model_dump(mode="json") | {
        "language": language,
        "expected_raw_sha256": digest(text),
        "expected_text_sha256": digest(text),
    }
    import json

    record = ingest_document(SourceManifest.model_validate_json(json.dumps(data)), text, text)
    assert record.quality.eligible
    assert "parser_language_unsupported" in record.quarantine_reasons
    assert not record.eligible_for_retrieval
