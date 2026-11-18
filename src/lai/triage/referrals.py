"""Offline referral register: pending, stale and future evidence is never displayed."""

from datetime import date
from importlib.resources import files
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from lai.corpus.models import Contract, Identifier, Sha256, Source
from lai.triage.contracts import Urgency

ReferralKind = Literal["legal_aid", "regional", "emergency", "attorney_review"]
SOURCE_HOSTS: dict[ReferralKind, set[str]] = {
    "legal_aid": {"moj.gov.lk", "legalaid.gov.lk"},
    "regional": {"moj.gov.lk", "legalaid.gov.lk"},
    "attorney_review": {"basl.lk"},
    "emergency": {
        "moj.gov.lk",
        "police.lk",
        "childprotection.gov.lk",
        "nimh.health.gov.lk",
        "1990.lk",
    },
}
Phone = Annotated[str, Field(pattern=r"^\+?[0-9][0-9 ()-]{1,28}[0-9]$")]
Channel = Literal[
    "general_office",
    "regional_counter",
    "emergency_response",
    "complaints",
    "specialist_support",
    "mental_health_support",
]
Caution = Literal[
    "published_listing_only",
    "availability_not_call_tested",
    "regional_phone_withheld",
    "general_office_only",
    "no_review_commitment",
    "complaints_not_emergency_response",
    "directory_text_has_repetition",
]


class Referral(Contract):
    id: Identifier
    kind: ReferralKind
    organisation: str
    source_url: str
    attempted_on: date
    status: Literal["UNVERIFIED", "VERIFIED"] = "UNVERIFIED"
    blocker: str | None = None
    verified_on: date | None = None
    review_due: date | None = None
    source_sha256: Sha256 | None = None
    verification_method: Literal["primary_source_inspection"] | None = None
    service_description: str | None = None
    region: str | None = None
    address: str | None = None
    phone: Phone | None = None
    additional_phones: tuple[Phone, ...] = ()
    hours: str | None = None
    channel: Channel | None = None
    urgent_categories: tuple[Urgency, ...] = ()
    cautions: tuple[Caution, ...] = ()
    directory_url: str | None = None
    directory_sha256: Sha256 | None = None

    @model_validator(mode="after")
    def verify_evidence(self) -> Self:
        Source.public_source_url(self.source_url)
        host = urlsplit(self.source_url).hostname
        allowed = SOURCE_HOSTS[self.kind] | {"www." + host for host in SOURCE_HOSTS[self.kind]}
        if host not in allowed or urlsplit(self.source_url).scheme != "https":
            raise ValueError("referral_requires_official_https_source")
        evidence = (self.verified_on, self.review_due, self.source_sha256, self.verification_method)
        details = (
            self.service_description,
            self.region,
            self.address,
            self.phone,
            self.hours,
            self.additional_phones,
            self.channel,
            self.directory_url,
            self.directory_sha256,
        )
        if self.status == "UNVERIFIED":
            if any(evidence) or any(details) or not self.blocker:
                raise ValueError("unverified_referral_must_withhold_details")
        elif (
            not all(evidence)
            or self.blocker is not None
            or not self.service_description
            or not self.channel
            or not self.cautions
            or self.verified_on is None
            or self.review_due is None
            or self.verified_on > self.review_due
            or (self.review_due - self.verified_on).days > 90
            or self.attempted_on != self.verified_on
        ):
            raise ValueError("referral_verification_incomplete")
        if self.additional_phones and self.phone is None:
            raise ValueError("additional_phones_require_primary")
        if len(set(self.urgent_categories)) != len(self.urgent_categories):
            raise ValueError("duplicate_urgent_category")
        if self.kind != "emergency" and self.urgent_categories:
            raise ValueError("urgent_categories_require_emergency_kind")
        if self.status == "VERIFIED":
            if self.kind == "emergency" and (
                not self.urgent_categories
                or self.channel
                not in {
                    "emergency_response",
                    "complaints",
                    "specialist_support",
                    "mental_health_support",
                }
            ):
                raise ValueError("emergency_scope_required")
            if self.kind == "regional":
                if not self.region or not self.address or self.channel != "regional_counter":
                    raise ValueError("regional_location_required")
                if not self.directory_url or not self.directory_sha256:
                    raise ValueError("regional_directory_evidence_required")
                Source.public_source_url(self.directory_url)
                url = urlsplit(self.directory_url)
                if (
                    url.scheme != "https"
                    or url.hostname != "www.google.com"
                    or url.path != "/maps/d/kml"
                ):
                    raise ValueError("directory_source_not_approved")
            elif self.directory_url or self.directory_sha256:
                raise ValueError("unexpected_directory_evidence")
            if self.kind in {"legal_aid", "attorney_review"} and self.channel != "general_office":
                raise ValueError("general_office_channel_required")
        return self


class ReferralRegister(Contract):
    schema_version: Literal["2"] = "2"
    revision: str
    records: tuple[Referral, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> Self:
        if len({item.id for item in self.records}) != len(self.records):
            raise ValueError("duplicate_referral")
        return self


def load_referrals() -> ReferralRegister:
    return ReferralRegister.model_validate_json(
        files("lai.triage").joinpath("data/referrals.json").read_bytes()
    )


def active_referrals(
    kinds: tuple[ReferralKind, ...],
    as_of: date,
    register: ReferralRegister | None = None,
    *,
    urgency: tuple[Urgency, ...] = (),
    region: str | None = None,
) -> tuple[Referral, ...]:
    register = register or load_referrals()
    return tuple(
        item
        for item in register.records
        if item.kind in kinds
        and item.status == "VERIFIED"
        and item.verified_on is not None
        and item.review_due is not None
        and item.verified_on <= as_of <= item.review_due
        and (item.kind != "emergency" or bool(set(item.urgent_categories).intersection(urgency)))
        and (
            region is None
            or item.kind != "regional"
            or item.region is not None
            and item.region.casefold() == region.casefold()
        )
    )
