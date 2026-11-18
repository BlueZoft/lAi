"""Synthetic bytes exercise integrity and path boundaries without network."""

import json
from datetime import date
from hashlib import sha256
from pathlib import Path

import pytest

from lai.triage.evidence import audit
from lai.triage.referrals import Referral, ReferralRegister

pytestmark = pytest.mark.safety


@pytest.mark.parametrize("damage", ["none", "changed_bytes", "path_escape", "wrong_source"])
def test_source_audit_rejects_corruption_and_unbound_observations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    body = b"<p>SYNTHETIC source listing; no contact numbers.</p>"
    checksum = sha256(body).hexdigest()
    (tmp_path / "source.html").write_bytes(body)
    source = {
        "url": "https://moj.gov.lk/",
        "file": "source.html",
        "sha256": checksum,
        "observed_on": "2026-11-19",
    }
    record = Referral(
        id="synthetic",
        kind="legal_aid",
        organisation="SYNTHETIC TEST",
        source_url=source["url"],
        attempted_on=date(2026, 11, 19),
        status="VERIFIED",
        verified_on=date(2026, 11, 19),
        review_due=date(2026, 12, 19),
        source_sha256=checksum,
        verification_method="primary_source_inspection",
        service_description="SYNTHETIC metadata, not an actual service",
        channel="general_office",
        cautions=("published_listing_only",),
    )
    monkeypatch.setattr(
        "lai.triage.evidence.load_referrals",
        lambda: ReferralRegister(revision="synthetic", records=(record,)),
    )
    if damage == "changed_bytes":
        (tmp_path / "source.html").write_bytes(b"SYNTHETIC changed source")
    elif damage == "path_escape":
        source["file"] = "../outside.html"
    elif damage == "wrong_source":
        source["url"] = "https://legalaid.gov.lk/"
    (tmp_path / "manifest.json").write_text(json.dumps({"sources": [source]}))
    if damage == "none":
        assert audit(tmp_path) == (1, 0)
    else:
        with pytest.raises(ValueError):
            audit(tmp_path)
