"""Synthetic metadata assertions do not establish real referral verification or review."""

import json
from datetime import date

import pytest
from pydantic import ValidationError

from lai.triage.contracts import NavigationOutcome, TriageDecision
from lai.triage.referrals import Referral, ReferralRegister, active_referrals, load_referrals
from lai.triage.rules import decide
from lai.triage.templates import SafetyTemplate, SafetyTemplates, approved_messages, load_templates

pytestmark = pytest.mark.safety
AS_OF = date(2026, 11, 18)


def synthetic_verified() -> dict[str, object]:
    return {
        "id": "synthetic-source-check",
        "kind": "legal_aid",
        "organisation": "SYNTHETIC TEST",
        "source_url": "https://moj.gov.lk/",
        "attempted_on": "2026-11-18",
        "status": "VERIFIED",
        "verified_on": "2026-11-18",
        "review_due": "2026-12-18",
        "source_sha256": "0" * 64,
        "verification_method": "primary_source_inspection",
        "service_description": "SYNTHETIC metadata for validator testing only",
    }


def test_pending_register_withholds_all_contact_details() -> None:
    register = load_referrals()
    assert {item.kind for item in register.records} == {
        "legal_aid",
        "regional",
        "emergency",
        "attorney_review",
    }
    assert all(item.status == "UNVERIFIED" and item.blocker for item in register.records)
    assert not active_referrals(("legal_aid", "regional", "emergency", "attorney_review"), AS_OF)
    for item in register.records:
        assert not any(
            (item.address, item.phone, item.hours, item.region, item.service_description)
        )


@pytest.mark.parametrize("field", ["phone", "address", "region", "hours", "service_description"])
def test_unverified_record_cannot_smuggle_contact_details(field: str) -> None:
    pending = load_referrals().records[0].model_dump(mode="json")
    pending[field] = "SYNTHETIC withheld detail"
    with pytest.raises(ValidationError):
        Referral.model_validate_json(json.dumps(pending))


@pytest.mark.parametrize(
    "change",
    [
        {"source_sha256": None},
        {"verified_on": None},
        {"verification_method": None},
        {"blocker": "UNVERIFIED"},
        {"review_due": "2026-11-01"},
        {"review_due": "2027-11-18"},
        {"source_url": "https://example.invalid/"},
        {"source_url": "http://moj.gov.lk/"},
        {"source_url": "https://moj.gov.lk/?token=synthetic"},
        {"kind": "attorney_review"},
        {"attempted_on": "2026-11-17"},
    ],
)
def test_verified_metadata_requires_full_primary_source_evidence(change: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Referral.model_validate_json(json.dumps(synthetic_verified() | change))


def test_future_stale_and_wrong_kind_records_are_hidden() -> None:
    record = Referral.model_validate_json(json.dumps(synthetic_verified()))
    register = ReferralRegister(revision="synthetic", records=(record,))
    assert not active_referrals(("legal_aid",), date(2026, 11, 17), register)
    assert active_referrals(("legal_aid",), AS_OF, register) == (record,)
    assert active_referrals(("legal_aid",), date(2026, 12, 18), register) == (record,)
    assert not active_referrals(("legal_aid",), date(2026, 12, 19), register)
    assert not active_referrals(("emergency",), AS_OF, register)
    with pytest.raises(ValidationError, match="duplicate_referral"):
        ReferralRegister(revision="synthetic", records=(record, record))


def test_all_fixed_templates_are_present_in_both_languages_and_unreviewed() -> None:
    register = load_templates()
    assert len(register.templates) == 12
    assert all(item.review_status == "UNREVIEWED" for item in register.templates)
    for language in ("en", "si"):
        assert approved_messages(decide({"text": "deadline"}), language, AS_OF) == ()
    limitation = next(
        item.text
        for item in register.templates
        if item.id == "limitation" and item.language == "en"
    )
    assert "may already have expired" in limitation and "now" in limitation


@pytest.mark.parametrize(
    "change",
    [
        {"review_status": "APPROVED"},
        {"attorney_reviewed_on": "2026-11-18"},
        {"text": "Do something about {query}"},
    ],
)
def test_template_review_and_interpolation_bypasses_are_rejected(change: dict[str, object]) -> None:
    record = load_templates().templates[0].model_dump(mode="json")
    with pytest.raises(ValidationError):
        SafetyTemplate.model_validate_json(json.dumps(record | change))


def test_review_is_all_or_nothing_for_every_selected_message() -> None:
    decision = decide({"text": "deadline"})
    data = load_templates().model_dump(mode="json")
    for template in data["templates"]:
        if template["id"] in decision.template_ids and template["language"] == "en":
            template.update(
                review_status="APPROVED",
                attorney_reviewed_on="2026-11-18",
                language_reviewed_on="2026-11-18",
            )
    register = SafetyTemplates.model_validate_json(json.dumps(data))
    assert len(approved_messages(decision, "en", AS_OF, register)) == 2
    assert not approved_messages(decision, "si", AS_OF, register)
    assert not approved_messages(decision, "en", date(2026, 11, 17), register)
    data["templates"].pop()
    with pytest.raises(ValidationError, match="safety_template_set_incomplete"):
        SafetyTemplates.model_validate_json(json.dumps(data))


def test_decision_cannot_allow_urgent_limitation_or_sensitive_navigation() -> None:
    with pytest.raises(ValidationError, match="urgency_requires_immediate"):
        TriageDecision(
            action="navigate",
            urgency=("self_harm",),
            reasons=("synthetic",),
            template_ids=("urgent",),
        )
    with pytest.raises(ValidationError, match="limitation_requires_professional"):
        TriageDecision(
            action="navigate",
            limitation_warning=True,
            reasons=("synthetic",),
            template_ids=("limitation",),
        )
    with pytest.raises(ValidationError, match="navigation_domain_not_allowed"):
        TriageDecision(
            action="navigate",
            domains=("employment",),
            reasons=("synthetic",),
            template_ids=("extractive",),
        )
    from lai.retrieval.models import RetrievalResult

    with pytest.raises(ValidationError, match="blocked_route_has_downstream_result"):
        NavigationOutcome(
            decision=decide({"text": "self harm"}), retrieval=RetrievalResult(status="abstained")
        )
