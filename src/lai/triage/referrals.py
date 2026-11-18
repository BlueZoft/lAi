"""Offline referral register: pending, stale and future evidence is never displayed."""

from datetime import date
from importlib.resources import files
from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from lai.corpus.models import Contract, Identifier, Sha256, Source

ReferralKind = Literal["legal_aid", "regional", "emergency", "attorney_review"]
OFFICIAL_HOSTS = {
    "moj.gov.lk",
    "www.moj.gov.lk",
    "legalaid.gov.lk",
    "www.legalaid.gov.lk",
    "basl.lk",
    "www.basl.lk",
}


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
    phone: str | None = Field(default=None, pattern=r"^\+?[0-9 ()-]{3,30}$")
    hours: str | None = None

    @model_validator(mode="after")
    def verify_evidence(self) -> Self:
        Source.public_source_url(self.source_url)
        host = urlsplit(self.source_url).hostname
        allowed = (
            {"basl.lk", "www.basl.lk"}
            if self.kind == "attorney_review"
            else OFFICIAL_HOSTS - {"basl.lk", "www.basl.lk"}
        )
        if host not in allowed or urlsplit(self.source_url).scheme != "https":
            raise ValueError("referral_requires_official_https_source")
        evidence = (self.verified_on, self.review_due, self.source_sha256, self.verification_method)
        details = (self.service_description, self.region, self.address, self.phone, self.hours)
        if self.status == "UNVERIFIED":
            if any(evidence) or any(details) or not self.blocker:
                raise ValueError("unverified_referral_must_withhold_details")
        elif (
            not all(evidence)
            or self.blocker is not None
            or not self.service_description
            or self.verified_on is None
            or self.review_due is None
            or self.verified_on > self.review_due
            or (self.review_due - self.verified_on).days > 90
            or self.attempted_on != self.verified_on
        ):
            raise ValueError("referral_verification_incomplete")
        return self


class ReferralRegister(Contract):
    schema_version: Literal["1"] = "1"
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
    )
