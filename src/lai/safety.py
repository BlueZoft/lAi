"""Release prerequisites, independent of retrieval and model adapters."""

from pydantic import BaseModel, ConfigDict


class LaunchGate(BaseModel):
    """All evidence must be supplied explicitly before a public release is considered."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    attorney_taxonomy_reviewed: bool = False
    attorney_glosses_reviewed: bool = False
    attorney_escalations_reviewed: bool = False
    dpia_complete: bool = False
    golden_set_passed: bool = False
    offered_domain_gaps_closed: bool = False
    institutional_partner_engaged: bool = False
    service_free: bool = False
    clearly_non_authoritative: bool = False
    referral_first: bool = False

    def allows_public_launch(self) -> bool:
        """Represent the brief's release condition without inferring evidence."""
        reviewed_and_measured = all(
            (
                self.attorney_taxonomy_reviewed,
                self.attorney_glosses_reviewed,
                self.attorney_escalations_reviewed,
                self.dpia_complete,
                self.golden_set_passed,
                self.offered_domain_gaps_closed,
            )
        )
        delivery_condition = self.institutional_partner_engaged or all(
            (self.service_free, self.clearly_non_authoritative, self.referral_first)
        )
        return reviewed_and_measured and delivery_condition
