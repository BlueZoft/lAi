from typing import Literal, Self

from pydantic import Field, model_validator

from lai.corpus.models import Contract
from lai.retrieval.models import RetrievalResult

Urgency = Literal[
    "domestic_violence",
    "child_protection",
    "sexual_violence",
    "unlawful_detention",
    "imminent_destitution",
    "self_harm",
]
Domain = Literal[
    "procedural_administrative",
    "employment",
    "land",
    "family",
    "debt",
    "criminal",
    "substantive_rights",
    "unknown",
]
Action = Literal["immediate_escalation", "professional_referral", "refuse", "abstain", "navigate"]
TemplateId = Literal["urgent", "refuse", "professional", "limitation", "abstain", "extractive"]


class UrgentSignals(Contract):
    domestic_violence: bool = False
    child_protection: bool = False
    sexual_violence: bool = False
    unlawful_detention: bool = False
    imminent_destitution: bool = False
    self_harm: bool = False


class TriageRequest(Contract):
    text: str = Field(min_length=1, max_length=1024)
    language: Literal["en", "si", "ta", "si-Latn"] = "en"
    urgent: UrgentSignals = Field(default_factory=UrgentSignals)


class SafetyPolicy(Contract):
    research_navigation_enabled: bool = False


class TriageDecision(Contract):
    rules_version: Literal["1"] = "1"
    action: Action
    urgency: tuple[Urgency, ...] = ()
    domains: tuple[Domain, ...] = ()
    limitation_warning: bool = False
    reasons: tuple[str, ...] = Field(min_length=1)
    template_ids: tuple[TemplateId, ...] = Field(min_length=1)
    referral_kinds: tuple[
        Literal["legal_aid", "regional", "emergency", "attorney_review"], ...
    ] = ()

    @model_validator(mode="after")
    def consistent_route(self) -> Self:
        if bool(self.urgency) != (self.action == "immediate_escalation"):
            raise ValueError("urgency_requires_immediate_escalation")
        if self.limitation_warning and self.action == "navigate":
            raise ValueError("limitation_requires_professional")
        if self.limitation_warning and "limitation" not in self.template_ids:
            raise ValueError("limitation_template_required")
        if self.action == "navigate" and self.domains != ("procedural_administrative",):
            raise ValueError("navigation_domain_not_allowed")
        return self


class NavigationOutcome(Contract):
    decision: TriageDecision
    retrieval: RetrievalResult | None = None

    @model_validator(mode="after")
    def blocked_results_empty(self) -> Self:
        if self.decision.action != "navigate" and self.retrieval is not None:
            raise ValueError("blocked_route_has_downstream_result")
        if self.decision.action == "navigate" and (
            self.retrieval is None or self.retrieval.status != "candidates"
        ):
            raise ValueError("navigation_requires_candidates")
        return self
