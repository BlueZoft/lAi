"""Versioned intake contracts. Source metadata never establishes legal effect."""

import hashlib
import json
from typing import Annotated, Literal, Self
from urllib.parse import parse_qs, urlsplit

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Identifier = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}$")]
Language = Literal["en", "si", "ta"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_id(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return digest(encoded.encode("utf-8"))


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Source(Contract):
    url: str = Field(min_length=1, max_length=2048, json_schema_extra={"format": "uri"})
    canonical_url: str | None = Field(
        default=None, min_length=1, max_length=2048, json_schema_extra={"format": "uri"}
    )
    publisher: str = Field(min_length=1, max_length=200)
    role: Literal["official", "mirror", "manual"]
    fetched_at: AwareDatetime
    revision: str = Field(min_length=1, max_length=200)
    licence: str = Field(min_length=1, max_length=200)
    metadata_reviewed: bool = False

    @field_validator("canonical_url")
    @classmethod
    def canonical_source_url(cls, value: str | None) -> str | None:
        return cls.public_source_url(value) if value is not None else None

    @field_validator("url")
    @classmethod
    def public_source_url(cls, value: str) -> str:
        url = urlsplit(value)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username
            or url.password
            or url.fragment
            or any(character.isspace() for character in value)
        ):
            raise ValueError("source_url_invalid")
        sensitive = {"token", "access_token", "key", "api_key", "signature", "sig"}
        if any(
            key.lower() in sensitive or key.lower().startswith("x-amz-")
            for key in parse_qs(url.query)
        ):
            raise ValueError("source_url_contains_credentials")
        return value


class Instrument(Contract):
    id: Identifier
    kind: Literal["act", "ordinance", "regulation", "bill", "gazette", "judgment"]
    number: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1700, le=2200)
    synthetic: bool = False


class Extraction(Contract):
    method: Literal["plain_text", "native_pdf", "ocr"]
    tool: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=100)
    fonts: tuple[str, ...] = Field(default=(), max_length=100)


class SourceManifest(Contract):
    schema_version: Literal["1"] = "1"
    source: Source
    instrument: Instrument
    language: Language
    expected_raw_sha256: Sha256
    expected_text_sha256: Sha256
    extraction: Extraction
    acquisition: Literal["upstream", "manual_seed", "synthetic"] = "upstream"
    gap_ids: tuple[Identifier, ...] = ()

    @model_validator(mode="after")
    def manual_seed_has_gap(self) -> Self:
        if self.acquisition == "manual_seed" and not self.gap_ids:
            raise ValueError("manual_seed_requires_gap_ids")
        if self.acquisition == "synthetic" and not self.instrument.synthetic:
            raise ValueError("synthetic_acquisition_requires_synthetic_instrument")
        return self


class QualityReport(Contract):
    policy_version: Literal["quality-v1"] = "quality-v1"
    score: float = Field(ge=0.0, le=1.0)
    character_count: int = Field(ge=0)
    alphabetic_ratio: float = Field(ge=0.0, le=1.0)
    declared_script_ratio: float = Field(ge=0.0, le=1.0)
    issues: tuple[str, ...]

    @property
    def eligible(self) -> bool:
        return not self.issues and self.score >= 0.8


class Section(Contract):
    number: str = Field(pattern=r"^[1-9][0-9]{0,3}[A-Z]{0,2}$")
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str = Field(min_length=1)
    text_sha256: Sha256

    @model_validator(mode="after")
    def validate_span(self) -> Self:
        if self.end <= self.start or self.end - self.start != len(self.text):
            raise ValueError("section_span_invalid")
        if digest(self.text.encode("utf-8")) != self.text_sha256:
            raise ValueError("section_hash_invalid")
        return self


class ParseResult(Contract):
    parser_version: Literal["act-sections-v1"] = "act-sections-v1"
    sections: tuple[Section, ...] = ()
    issues: tuple[str, ...] = ()


class IngestionRecord(Contract):
    schema_version: Literal["1"] = "1"
    record_id: Sha256
    manifest: SourceManifest
    quality: QualityReport
    parsed: ParseResult

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        payload = self.model_dump(mode="json", exclude={"record_id"})
        if content_id(payload) != self.record_id:
            raise ValueError("record_hash_invalid")
        sections = self.parsed.sections
        if len({section.number for section in sections}) != len(sections):
            raise ValueError("duplicate_section")
        if any(left.end > right.start for left, right in zip(sections, sections[1:], strict=False)):
            raise ValueError("overlapping_sections")
        return self

    @property
    def quarantine_reasons(self) -> tuple[str, ...]:
        reasons = list(self.quality.issues + self.parsed.issues)
        if not self.manifest.source.metadata_reviewed:
            reasons.append("source_unreviewed")
        if self.manifest.instrument.number is None or self.manifest.instrument.year is None:
            reasons.append("instrument_identity_incomplete")
        if not self.parsed.sections:
            reasons.append("no_sections")
        return tuple(sorted(set(reasons)))

    @property
    def eligible_for_retrieval(self) -> bool:
        return self.quality.eligible and not self.quarantine_reasons
