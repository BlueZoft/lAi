"""Conservative lexical rules, never a claim of exhaustive language coverage."""

import re
import unicodedata
from collections.abc import Mapping

from pydantic import ValidationError

from lai.retrieval.query import scripts_in
from lai.triage.contracts import (
    Domain,
    SafetyPolicy,
    TemplateId,
    TriageDecision,
    TriageRequest,
    Urgency,
)

URGENT_TERMS: dict[Urgency, tuple[str, ...]] = {
    "domestic_violence": (
        "domestic violence",
        "partner hit",
        "husband hit",
        "wife hit",
        "partner beat",
        "husband beat",
        "wife beat",
        "partner threatened",
        "unsafe at home",
        "being abused",
        "beating me",
        "hit me",
        "threatened to kill",
        "ගෘහස්ථ හිංස",
        "සැමියා මට පහර",
        "බිරිඳ මට පහර",
        "ගෙදර අනාරක්ෂිත",
        "குடும்ப வன்முறை",
        "வீட்டில் வன்முறை",
        "gedara gahanawa",
    ),
    "child_protection": (
        "child abuse",
        "child protection",
        "child being hurt",
        "child is being hurt",
        "child unsafe",
        "child marriage",
        "hurt my child",
        "abuse my child",
        "ළමා අපයෝජ",
        "දරුවාට පහර",
        "ළමා ආරක්ෂ",
        "குழந்தை துஷ்பிரயோகம்",
        "சிறுவர் பாதுகாப்பு",
        "lamayata gahanawa",
    ),
    "sexual_violence": (
        "sexual violence",
        "sexual assault",
        "sexually assaulted",
        "molested",
        "rape",
        "raped",
        "forced sex",
        "ලිංගික හිංස",
        "ලිංගික අතවර",
        "දූෂණය කළ",
        "பாலியல் வன்முறை",
        "பாலியல் பலாத்காரம்",
        "lingika athawara",
    ),
    "unlawful_detention": (
        "unlawful detention",
        "illegal detention",
        "detained without",
        "detained",
        "in custody",
        "arrested",
        "held without charge",
        "locked me up",
        "cannot leave police",
        "නීති විරෝධී රඳවා",
        "චෝදනා නැතිව රඳවා",
        "சட்டவிரோத காவல்",
        "குற்றச்சாட்டு இல்லாமல்",
        "nithi virodhi randawa",
    ),
    "imminent_destitution": (
        "imminent destitution",
        "homeless tonight",
        "no food today",
        "no shelter tonight",
        "nowhere to sleep",
        "nothing to eat",
        "evicted tonight",
        "starving",
        "අද කෑම නැහැ",
        "අද රෑ ඉන්න තැනක් නැහැ",
        "இன்று உணவு இல்லை",
        "இன்று தங்க இடமில்லை",
        "ada kanna naha",
    ),
    "self_harm": (
        "self harm",
        "self-harm",
        "suicide",
        "suicidal",
        "kill myself",
        "end my life",
        "do not want to live",
        "don't want to live",
        "hurt myself",
        "මැරෙන්න හිතෙනවා",
        "සියදිවි",
        "මටම හානි",
        "தற்கொலை",
        "என்னை கொல்ல",
        "marenna hithenawa",
    ),
}
DOMAIN_TERMS: dict[Domain, tuple[str, ...]] = {
    "procedural_administrative": (
        "document",
        "documents",
        "office",
        "form",
        "forms",
        "permit",
        "certificate",
        "fee",
        "fees",
        "processing time",
        "procedure",
        "register",
        "application",
        "ලේඛන",
        "කාර්යාල",
        "පෝරම",
        "බලපත්‍ර",
        "ගාස්තු",
        "සහතික",
        "ஆவணம்",
        "அலுவலகம்",
        "படிவம்",
        "கட்டணம்",
        "porma",
        "liyavili",
    ),
    "employment": (
        "employment",
        "employer",
        "salary",
        "wages",
        "dismissal",
        "fired",
        "රැකියා",
        "වැටුප්",
        "வேலை",
        "சம்பளம்",
    ),
    "land": ("land", "property", "deed", "boundary", "ඉඩම්", "ඔප්පු", "காணி", "நிலம்"),
    "family": ("divorce", "custody", "maintenance", "marriage", "දික්කසාද", "විවාහ", "விவாகரத்து"),
    "debt": ("debt", "loan", "creditor", "ණය", "கடன்"),
    "criminal": ("criminal", "arrest", "police", "bail", "plead", "අත්අඩංගු", "ඇප", "கைது", "பிணை"),
    "substantive_rights": (
        "rights",
        "liable",
        "entitled",
        "compensation",
        "අයිතිවාසිකම්",
        "වන්දි",
        "உரிமை",
    ),
}
FORBIDDEN_TERMS = (
    "legal conclusion",
    "am i liable",
    "am i guilty",
    "is this legal",
    "is this illegal",
    "will i win",
    "guarantees that i win",
    "should i sue",
    "should i",
    "legal advice",
    "recommend",
    "what do i do",
    "what can i do",
    "how do i defend",
    "write my defence",
    "draft my complaint",
    "what should i plead",
    "how should i plead",
    "draft my pleading",
    "draft my defence",
    "criminal defence",
    "criminal defense",
    "litigation strategy",
    "what should i sign",
    "should i sign",
    "advise me",
    "tell me what to do",
    "calculate my deadline",
    "නඩුව දිනයිද",
    "අත්සන් කරන්නද",
    "මා වැරදිකරුද",
    "கையெழுத்திடலாமா",
    "வழக்கில் வெற்றி",
)
LIMITATION_TERMS = (
    "limitation",
    "prescription",
    "time limit",
    "deadline",
    "last date",
    "out of time",
    "too late",
    "how long to sue",
    "කාල සීම",
    "කාලසීම",
    "අවසන් දිනය",
    "කල් ඉකුත්",
    "காலக்கெடு",
    "கால வரம்பு",
    "අවසන් දින",
    "kal seema",
)
INJECTION_TERMS = (
    "ignore previous",
    "ignore all",
    "ignore safety",
    "bypass",
    "system prompt",
    "developer message",
    "jailbreak",
    "pretend to be a lawyer",
    "act as a lawyer",
)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(char for char in text if unicodedata.category(char) != "Cf")
    return " ".join(text.split())


def contains(text: str, phrases: tuple[str, ...], *, obfuscated: bool = False) -> bool:
    for phrase in phrases:
        phrase = normalise(phrase)
        if phrase.isascii():
            pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
            if re.search(pattern, text):
                return True
            # Long multiword urgency phrases also survive spacing/punctuation/leet changes.
            if obfuscated and len(phrase.replace(" ", "")) >= 8 and " " in phrase:
                compact = re.sub(r"[^a-z]", "", text.translate(str.maketrans("013457", "oieast")))
                if re.sub(r"[^a-z]", "", phrase) in compact:
                    return True
        elif phrase in text:
            return True
    return False


def selected_templates(primary: TemplateId, limitation: bool) -> tuple[TemplateId, ...]:
    return (primary, "limitation") if limitation else (primary,)


def child_risk(text: str) -> bool:
    return contains(text, ("child", "minor", "baby", "son", "daughter")) and contains(
        text, ("abuse", "abused", "assault", "assaulted", "beaten", "unsafe", "neglect", "hurt")
    )


def decide(payload: object, policy: SafetyPolicy | None = None) -> TriageDecision:
    policy = policy or SafetyPolicy()
    # Read only bounded, known fields; malformed input never reaches the downstream path.
    raw = payload if isinstance(payload, Mapping) else {}
    supplied = raw.get("text")
    text = normalise(supplied[:4096]) if isinstance(supplied, str) else ""
    raw_signals = raw.get("urgent", {})
    signals = raw_signals if isinstance(raw_signals, Mapping) else {}
    urgent = tuple(
        key
        for key, terms in URGENT_TERMS.items()
        if signals.get(key) is True
        or contains(text, terms, obfuscated=True)
        or key == "child_protection"
        and child_risk(text)
    )
    limitation = contains(text, LIMITATION_TERMS)
    if urgent:
        return TriageDecision(
            action="immediate_escalation",
            urgency=urgent,
            limitation_warning=limitation,
            reasons=("urgent_signal",),
            template_ids=selected_templates("urgent", limitation),
            referral_kinds=("emergency", "legal_aid"),
        )
    try:
        request = TriageRequest.model_validate(payload)
    except ValidationError:
        return TriageDecision(
            action="abstain",
            reasons=("invalid_request",),
            limitation_warning=limitation,
            template_ids=selected_templates("abstain", limitation),
        )
    if not text or any(
        unicodedata.category(char) in {"Cc", "Cs", "Co"}
        and char not in "\n\r\t"
        or char == "\ufffd"
        for char in request.text
    ):
        return TriageDecision(
            action="abstain",
            reasons=("invalid_text",),
            limitation_warning=limitation,
            template_ids=selected_templates("abstain", limitation),
        )
    domains = tuple(key for key, terms in DOMAIN_TERMS.items() if contains(text, terms))
    domains = domains or ("unknown",)
    if contains(text, FORBIDDEN_TERMS) or contains(text, INJECTION_TERMS):
        return TriageDecision(
            action="refuse",
            domains=domains,
            limitation_warning=limitation,
            reasons=("forbidden_advice_or_instruction",),
            template_ids=selected_templates("refuse", limitation),
            referral_kinds=("legal_aid", "attorney_review"),
        )
    if limitation or any(
        domain not in {"procedural_administrative", "unknown"} for domain in domains
    ):
        return TriageDecision(
            action="professional_referral",
            domains=domains,
            limitation_warning=limitation,
            reasons=("limitation_flag" if limitation else "domain_requires_review",),
            template_ids=selected_templates("professional", limitation),
            referral_kinds=("legal_aid", "regional", "attorney_review"),
        )
    if (
        request.language in {"ta", "si-Latn"}
        or "unsupported" in scripts_in(text)
        or not scripts_in(text)
    ):
        return TriageDecision(
            action="abstain",
            domains=domains,
            reasons=("language_coverage_unverified",),
            template_ids=("abstain",),
        )
    if domains == ("procedural_administrative",) and policy.research_navigation_enabled:
        return TriageDecision(
            action="navigate",
            domains=domains,
            reasons=("private_procedural_navigation",),
            template_ids=("extractive",),
        )
    return TriageDecision(
        action="abstain",
        domains=domains,
        reasons=("navigation_disabled_or_unknown",),
        template_ids=("abstain",),
    )
