import pytest

from lai.retrieval.query import plan_query, tokens


class FixtureTransliterator:
    def transliterate(self, text: str) -> str | None:
        return {"porma": "පෝරම"}.get(text)


class UnavailableTransliterator:
    def transliterate(self, text: str) -> str | None:
        raise RuntimeError("SYNTHETIC_SENSITIVE_SENTINEL")


@pytest.mark.parametrize(
    ("query", "script"),
    [
        ("SYNTHETIC Forms", "latin"),
        ("පෝරම", "sinhala"),
        ("படிவம்", "tamil"),
    ],
)
def test_native_scripts_are_preserved(query: str, script: str) -> None:
    plan = plan_query(query)
    assert plan.scripts == (script,)
    assert len(plan.variants) == 1
    assert tokens(query)


def test_mixed_scripts_and_combining_marks_are_supported() -> None:
    plan = plan_query("  පෝරම  FORM  ")
    assert plan.variants == ("පෝරම form",)
    assert plan.warnings == ("mixed_script",)
    assert tokens("தமிழ்") == ("தமிழ்",)


def test_singlish_uses_only_explicit_bounded_adapter() -> None:
    with pytest.raises(ValueError, match="transliteration_unavailable"):
        plan_query("porma", "si-Latn")
    plan = plan_query("porma", "si-Latn", FixtureTransliterator())
    assert plan.variants == ("porma", "පෝරම")
    with pytest.raises(ValueError, match="transliteration_unavailable"):
        plan_query("unmapped synthetic input", "si-Latn", FixtureTransliterator())
    with pytest.raises(ValueError, match="^transliteration_unavailable$"):
        plan_query("porma", "si-Latn", UnavailableTransliterator())


@pytest.mark.parametrize(
    "query",
    ["", " ", "9", "\x00forms", "\ud800", "\ue001", "\ufffd", "\u202eforms", "x" * 1025, "Пример"],
)
def test_malformed_or_unsupported_query_is_rejected(query: str) -> None:
    with pytest.raises(ValueError):
        plan_query(query)


def test_language_hint_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="query_language_hint_mismatch"):
        plan_query("synthetic English", "ta")
