"""English Act sections with exact code-point spans into unmodified extraction."""

import re

from lai.corpus.models import Instrument, Language, ParseResult, Section, digest

SECTION = re.compile(
    r"^[ \t]*([1-9][0-9]{0,3}[A-Z]{0,2})\.(?=[ \t(\-\u2013\u2014]|$)", re.MULTILINE
)
SCHEDULE = re.compile(
    r"^[ \t]*(?:(?:FIRST|SECOND|THIRD|FOURTH|FIFTH)\s+)?SCHEDULE(?:S|\s+[IVX0-9]+)?[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)
STRUCTURE = re.compile(r"^[ \t]*(?:PART|CHAPTER)\s+[IVXLC0-9]+(?:[ \t]+[^\n]*)?$", re.MULTILINE)


def section_order(label: str) -> tuple[int, int]:
    match = re.fullmatch(r"([0-9]+)([A-Z]*)", label)
    if match is None:
        raise ValueError("section_label_invalid")
    suffix = 0
    for character in match[2]:
        suffix = suffix * 26 + ord(character) - ord("A") + 1
    return int(match[1]), suffix


def parse_act(text: str, language: Language, instrument: Instrument) -> ParseResult:
    if language != "en":
        return ParseResult(issues=("parser_language_unsupported",))
    if instrument.kind not in {"act", "ordinance"}:
        return ParseResult(issues=("parser_instrument_unsupported",))
    schedule = SCHEDULE.search(text)
    end = schedule.start() if schedule else len(text)
    matches = list(SECTION.finditer(text, endpos=end))
    issues: set[str] = set()
    if schedule:
        issues.add("schedules_require_review")
    if not matches:
        return ParseResult(issues=tuple(sorted(issues | {"no_sections"})))
    labels = [match[1] for match in matches]
    if len(set(labels)) != len(labels):
        return ParseResult(issues=tuple(sorted(issues | {"duplicate_section_numbers"})))
    orders = [section_order(label) for label in labels]
    if orders[0] != (1, 0):
        issues.add("first_section_missing")
    if orders != sorted(orders):
        issues.add("section_order_invalid")
    if any(right[0] > left[0] + 1 for left, right in zip(orders, orders[1:], strict=False)):
        issues.add("section_number_gap")
    sections: list[Section] = []
    for index, match in enumerate(matches):
        start = match.start(1)
        stop = matches[index + 1].start() if index + 1 < len(matches) else end
        structure = STRUCTURE.search(text, match.end(), stop)
        if structure:
            stop = structure.start()
        while stop > start and text[stop - 1].isspace():
            stop -= 1
        section_text = text[start:stop]
        if len(section_text[match.end(1) - start + 1 :].strip()) < 5:
            issues.add("section_text_too_short")
        sections.append(
            Section(
                number=match[1],
                start=start,
                end=stop,
                text=section_text,
                text_sha256=digest(section_text.encode("utf-8")),
            )
        )
    return ParseResult(sections=tuple(sections), issues=tuple(sorted(issues)))
