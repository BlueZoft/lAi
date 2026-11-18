"""Unicode handling and a bounded, explicitly supplied Singlish adapter."""

import unicodedata
from dataclasses import dataclass
from typing import Literal, Protocol

LanguageHint = Literal["en", "si", "ta", "si-Latn"]


class Transliterator(Protocol):
    def transliterate(self, text: str) -> str | None: ...


@dataclass(frozen=True)
class QueryPlan:
    variants: tuple[str, ...]
    scripts: tuple[str, ...]
    warnings: tuple[str, ...]


def tokens(text: str) -> tuple[str, ...]:
    words: list[str] = []
    current: list[str] = []
    for character in unicodedata.normalize("NFC", text).casefold():
        if (
            character.isalnum()
            or unicodedata.category(character).startswith("M")
            or character in "\u200c\u200d"
        ):
            current.append(character)
        elif current:
            words.append("".join(current))
            current = []
    if current:
        words.append("".join(current))
    return tuple(words)


def scripts_in(text: str) -> tuple[str, ...]:
    scripts: set[str] = set()
    for character in text:
        if not character.isalpha():
            continue
        if "\u0d80" <= character <= "\u0dff":
            scripts.add("sinhala")
        elif "\u0b80" <= character <= "\u0bff":
            scripts.add("tamil")
        elif "LATIN" in unicodedata.name(character, ""):
            scripts.add("latin")
        else:
            scripts.add("unsupported")
    return tuple(sorted(scripts))


def plan_query(
    text: str,
    hint: LanguageHint | None = None,
    transliterator: Transliterator | None = None,
) -> QueryPlan:
    if (
        not isinstance(text, str)
        or not text.strip()
        or len(text) > 1024
        or hint not in (None, "en", "si", "ta", "si-Latn")
    ):
        raise ValueError("invalid_query")
    if any(
        (unicodedata.category(character) in {"Cc", "Co", "Cs"} and character not in "\n\r\t")
        or character == "\ufffd"
        or (unicodedata.category(character) == "Cf" and character not in "\u200c\u200d")
        for character in text
    ):
        raise ValueError("invalid_query")
    normalised = " ".join(unicodedata.normalize("NFC", text).casefold().split())
    scripts = scripts_in(normalised)
    if not scripts or "unsupported" in scripts or len(tokens(normalised)) > 128:
        raise ValueError("unsupported_query")
    required_script = {"en": "latin", "si": "sinhala", "ta": "tamil"}.get(hint or "")
    if required_script is not None and required_script not in scripts:
        raise ValueError("query_language_hint_mismatch")
    warnings = ["mixed_script"] if len(scripts) > 1 else []
    variants = [normalised]
    if hint == "si-Latn":
        if scripts != ("latin",) or transliterator is None:
            raise ValueError("transliteration_unavailable")
        try:
            alternate = transliterator.transliterate(normalised)
        except Exception:
            raise ValueError("transliteration_unavailable") from None
        if (
            not isinstance(alternate, str)
            or len(alternate) > 1024
            or scripts_in(alternate) != ("sinhala",)
        ):
            raise ValueError("transliteration_unavailable")
        alternate_plan = plan_query(alternate)
        variants.extend(alternate_plan.variants)
        warnings.append("transliteration_requires_measurement")
    return QueryPlan(tuple(dict.fromkeys(variants)), scripts, tuple(warnings))
