"""Validate syntax and anchors. Semantic quality still requires human measurement."""

import json
import re
from datetime import date

from lai.model_tasks.contracts import (
    COMPLETION,
    Completion,
    EntitiesOutput,
    ExtractOutput,
    IntentOutput,
    LanguageOutput,
    RewriteOutput,
    Span,
    TaskRequest,
    TransliterationOutput,
)
from lai.retrieval.query import plan_query, scripts_in
from lai.triage.contracts import TriageDecision

DISTRICTS = frozenset(
    [
        "ampara",
        "anuradhapura",
        "badulla",
        "batticaloa",
        "colombo",
        "galle",
        "gampaha",
        "hambantota",
        "jaffna",
        "kalutara",
        "kandy",
        "kegalle",
        "kilinochchi",
        "kurunegala",
        "mannar",
        "matale",
        "matara",
        "monaragala",
        "mullaitivu",
        "nuwara eliya",
        "polonnaruwa",
        "puttalam",
        "ratnapura",
        "trincomalee",
        "vavuniya",
    ]
)


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key")
        result[key] = value
    return result


def script_result(request: TaskRequest) -> LanguageOutput:
    scripts = scripts_in(request.scenario.text)
    language = "und"
    if len(scripts) > 1:
        language = "mixed"
    elif scripts == ("sinhala",):
        language = "si"
    elif scripts == ("tamil",):
        language = "ta"
    elif scripts == ("latin",) and request.scenario.language in {"en", "si-Latn"}:
        language = request.scenario.language
    return LanguageOutput.model_validate({"scripts": scripts, "language": language})


def anchored(spans: tuple[Span, ...], text: str, maximum: int) -> None:
    previous = 0
    for span in spans:
        if span.start < previous or text[span.start : span.end] != span.text:
            raise ValueError("span_not_anchored_or_ordered")
        previous = span.end
    if sum(len(span.text) for span in spans) > maximum:
        raise ValueError("extract_too_long")


def validate_output(raw: bytes, request: TaskRequest, decision: TriageDecision) -> Completion:
    if not raw or len(raw) > 8192:
        raise ValueError("output_size")
    # Reject code fences, trailing prose, duplicate keys, NaN, wrong types and extra fields.
    data = json.loads(raw, object_pairs_hook=unique_object)
    output = COMPLETION.validate_json(json.dumps(data, allow_nan=False))
    if output.task != request.task:
        raise ValueError("wrong_task")
    text = request.scenario.text
    if isinstance(output, LanguageOutput):
        if output != script_result(request):
            raise ValueError("script_or_hint_disagreement")
    elif isinstance(output, TransliterationOutput):
        if scripts_in(text) != ("latin",) or scripts_in(output.text) != ("sinhala",):
            raise ValueError("wrong_transliteration_script")
        plan_query(output.text, "si")
        # Script validity cannot establish transliteration accuracy. Never enable product use.
    elif isinstance(output, IntentOutput):
        if output.domain not in decision.domains and output.domain != "unknown":
            raise ValueError("intent_conflicts_with_rules")
    elif isinstance(output, EntitiesOutput):
        anchored(tuple(entity.span for entity in output.entities), text, 512)
        for entity in output.entities:
            value = entity.span.text
            if entity.kind == "date":
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
                    raise ValueError("ambiguous_date")
                date.fromisoformat(value)  # Validity only; never a deadline calculation.
            elif entity.kind == "amount":
                if not re.fullmatch(r"(?:LKR|Rs\.) [0-9]{1,9}(?:\.[0-9]{2})?", value):
                    raise ValueError("unsupported_amount")
            elif entity.kind == "district" and value.casefold() not in DISTRICTS:
                raise ValueError("district_alias_unreviewed")
            elif entity.kind == "employment_status" and value.casefold() not in {
                "employed",
                "unemployed",
                "self-employed",
            }:
                raise ValueError("employment_alias_unreviewed")
            # Prevent truncating e.g. an invalid date or a longer place/name into a valid value.
            before = text[entity.span.start - 1 : entity.span.start] if entity.span.start else ""
            after = text[entity.span.end : entity.span.end + 1]
            if (before and (before.isalnum() or before in "-._")) or (
                after and (after.isalnum() or after in "-._")
            ):
                raise ValueError("partial_entity")
    elif isinstance(output, RewriteOutput):
        anchored(output.spans, text, 256)
    elif isinstance(output, ExtractOutput):
        if request.source is None or output.source_sha256 != request.source.sha256:
            raise ValueError("wrong_source")
        anchored(output.spans, request.source.text, 768)
    return output
