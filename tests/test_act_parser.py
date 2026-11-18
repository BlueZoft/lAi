import pytest

from lai.corpus.models import SourceManifest
from lai.corpus.parser import parse_act


def test_subsections_and_inserted_sections_preserve_exact_text(
    source_manifest: SourceManifest,
) -> None:
    text = (
        "SYNTHETIC preamble\n1. Synthetic first section has a safe invented description.\n"
        " (1) This is a subsection and belongs to the first section.\n"
        "1A.—(1) Synthetic inserted section with an invented description.\n"
        "2. Synthetic second section with sufficient invented text.\n"
    )
    result = parse_act(text, "en", source_manifest.instrument)
    assert result.issues == ()
    assert [section.number for section in result.sections] == ["1", "1A", "2"]
    assert "subsection" in result.sections[0].text
    assert all(section.text == text[section.start : section.end] for section in result.sections)


def test_crlf_and_unicode_use_codepoint_offsets(
    source_manifest: SourceManifest,
    source_bytes: bytes,
) -> None:
    text = source_bytes.decode().replace("\n", "\r\n").replace("catalogue", "catalogue — සිංහල")
    result = parse_act(text, "en", source_manifest.instrument)
    assert result.issues == ()
    assert all(section.text == text[section.start : section.end] for section in result.sections)
    assert "\r\n" in result.sections[0].text


@pytest.mark.safety
@pytest.mark.parametrize(
    ("text", "issue"),
    [
        (
            "1. Synthetic first section.\n1. Synthetic repeated section.",
            "duplicate_section_numbers",
        ),
        ("1. Synthetic first section.\n3. Synthetic missing section.", "section_number_gap"),
        ("2. Synthetic second section.\n1. Synthetic first section.", "section_order_invalid"),
        ("2. Synthetic fragment only.", "first_section_missing"),
        ("SYNTHETIC text with no recognisable section heading", "no_sections"),
        (
            "1. Synthetic first section.\nSCHEDULE\n1. Synthetic schedule item.",
            "schedules_require_review",
        ),
    ],
)
def test_incomplete_or_ambiguous_structure_is_flagged(
    source_manifest: SourceManifest,
    text: str,
    issue: str,
) -> None:
    assert issue in parse_act(text, "en", source_manifest.instrument).issues


def test_decimal_list_and_inline_references_do_not_create_sections(
    source_manifest: SourceManifest,
) -> None:
    text = (
        "1. Synthetic first section containing a reference to section 7.\n"
        "1.1 this is a decimal list item within the first section.\n"
        "2. Synthetic second section describes another invented record.\n"
    )
    result = parse_act(text, "en", source_manifest.instrument)
    assert result.issues == ()
    assert len(result.sections) == 2
    assert "1.1" in result.sections[0].text


def test_non_act_sources_require_separate_parser(source_manifest: SourceManifest) -> None:
    instrument = source_manifest.instrument.model_copy(update={"kind": "judgment"})
    result = parse_act("1. SYNTHETIC document", "en", instrument)
    assert result.issues == ("parser_instrument_unsupported",)
