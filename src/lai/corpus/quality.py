"""Conservative extraction heuristics. Scores are not calibrated OCR accuracy."""

import re
import unicodedata

from lai.corpus.models import Extraction, Language, QualityReport

LEGACY_FONTS = ("fmabhaya", "dlmanel", "fmderana", "dlparas")
MOJIBAKE = (
    "\u00e0\u00b6",
    "\u00e0\u00b7",
    "\u00e0\u00ae",
    "\u00e0\u00af",
    "\u00e2\u20ac",
    "\u00c3\u00a2",
)


def assess_text(text: str, language: Language, extraction: Extraction) -> QualityReport:
    visible = [character for character in text if not character.isspace()]
    alphabetic = [character for character in visible if character.isalpha()]
    non_combining = [
        character for character in visible if not unicodedata.category(character).startswith("M")
    ]
    alpha_ratio = len(alphabetic) / max(len(non_combining), 1)
    if language == "si":
        script_count = sum("\u0d80" <= character <= "\u0dff" for character in alphabetic)
    elif language == "ta":
        script_count = sum("\u0b80" <= character <= "\u0bff" for character in alphabetic)
    else:
        script_count = sum("LATIN" in unicodedata.name(character, "") for character in alphabetic)
    script_ratio = script_count / max(len(alphabetic), 1)
    issues: list[str] = []
    if not visible:
        issues.append("empty_text")
    if len(visible) < 80:
        issues.append("text_too_short")
    if alpha_ratio < 0.5:
        issues.append("low_alphabetic_ratio")
    if script_ratio < 0.3:
        issues.append("declared_script_mismatch")
    if "\ufffd" in text:
        issues.append("replacement_character")
    if any(unicodedata.category(character) == "Co" for character in text):
        issues.append("private_use_glyphs")
    if any(
        unicodedata.category(character) == "Cc" and character not in "\n\r\t\f"
        for character in text
    ):
        issues.append("control_characters")
    if any(sequence in text for sequence in MOJIBAKE):
        issues.append("mojibake")
    if any(match[1].isalpha() for match in re.finditer(r"([^\s\d])\1{11,}", text)):
        issues.append("repeated_glyphs")
    fonts = [re.sub(r"[^a-z0-9]", "", font.lower()) for font in extraction.fonts]
    if any(legacy in font for legacy in LEGACY_FONTS for font in fonts):
        issues.append("legacy_font")
    score = round(max(0.0, min(alpha_ratio / 0.7, 1.0) - 0.25 * len(issues)), 4)
    return QualityReport(
        score=score,
        character_count=len(text),
        alphabetic_ratio=round(alpha_ratio, 4),
        declared_script_ratio=round(script_ratio, 4),
        issues=tuple(sorted(issues)),
    )
