"""Release prerequisites remain closed without explicit evidence for every condition."""

import pytest
from pydantic import ValidationError

from lai.safety import LaunchGate

pytestmark = pytest.mark.safety

REVIEW_REQUIREMENTS = (
    "attorney_taxonomy_reviewed",
    "attorney_glosses_reviewed",
    "attorney_escalations_reviewed",
    "dpia_complete",
    "golden_set_passed",
    "offered_domain_gaps_closed",
)
FREE_SERVICE_REQUIREMENTS = ("service_free", "clearly_non_authoritative", "referral_first")


def reviewed_evidence() -> dict[str, bool]:
    return dict.fromkeys(REVIEW_REQUIREMENTS, True)


def test_launch_is_closed_by_default() -> None:
    assert not LaunchGate().allows_public_launch()


@pytest.mark.parametrize("missing", REVIEW_REQUIREMENTS)
def test_partner_cannot_bypass_any_review_or_measurement(missing: str) -> None:
    evidence = reviewed_evidence() | {"institutional_partner_engaged": True, missing: False}
    assert not LaunchGate.model_validate(evidence).allows_public_launch()


@pytest.mark.parametrize("missing", REVIEW_REQUIREMENTS)
def test_free_service_cannot_bypass_any_review_or_measurement(missing: str) -> None:
    evidence = reviewed_evidence() | dict.fromkeys(FREE_SERVICE_REQUIREMENTS, True)
    evidence[missing] = False
    assert not LaunchGate.model_validate(evidence).allows_public_launch()


@pytest.mark.parametrize("missing", FREE_SERVICE_REQUIREMENTS)
def test_alternative_delivery_condition_requires_all_three(missing: str) -> None:
    evidence = reviewed_evidence() | dict.fromkeys(FREE_SERVICE_REQUIREMENTS, True)
    evidence[missing] = False
    assert not LaunchGate.model_validate(evidence).allows_public_launch()


def test_reviews_alone_are_insufficient() -> None:
    assert not LaunchGate.model_validate(reviewed_evidence()).allows_public_launch()


def test_partner_path_with_all_reviews() -> None:
    evidence = reviewed_evidence() | {"institutional_partner_engaged": True}
    assert LaunchGate.model_validate(evidence).allows_public_launch()


def test_free_referral_path_with_all_reviews() -> None:
    evidence = reviewed_evidence() | dict.fromkeys(FREE_SERVICE_REQUIREMENTS, True)
    assert LaunchGate.model_validate(evidence).allows_public_launch()


@pytest.mark.parametrize("value", ["true", "false", 1, 0, None, [], {}])
def test_untrusted_evidence_cannot_coerce_a_boolean(value: object) -> None:
    with pytest.raises(ValidationError):
        LaunchGate.model_validate({"dpia_complete": value})


def test_unknown_evidence_is_rejected() -> None:
    with pytest.raises(ValidationError):
        LaunchGate.model_validate({"model_says_safe": True})
