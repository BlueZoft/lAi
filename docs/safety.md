# Deterministic safety routing

T4 is a private engineering implementation. `SafetyNavigator.handle` is the
entry contract for future product requests. It calls `decide` before entering
the entire downstream analysis/model/retrieval path. The HTTP API still exposes
health. T5 must integrate through this gate; the T3 evaluation CLI remains an
operator-only research tool. README's full launch gate applies throughout.

```sh
make setup
make verify
make safety
```

## Routing precedence and scope

| Priority | Signal | Result |
| --- | --- | --- |
| 1 | Any of the six urgent classes, including an explicit true checkbox | Immediate escalation; downstream never runs |
| 2 | Malformed request or unusable text | Closed abstention; downstream never runs |
| 3 | Forbidden advice or prompt override | Fixed refusal and professional route |
| 4 | Limitation/time-limit question or gated substantive domain | Professional route and mandatory limitation flag where detected |
| 5 | Unsupported language/script or unknown scenario | Closed abstention |
| 6 | Procedural/administrative scope with explicit private research enablement | T3 retrieval through the injected downstream interface |
| Default | Navigation disabled | Closed abstention |

The urgent classes are domestic violence, child protection, sexual violence,
unlawful detention, imminent destitution and self-harm. These are technical
routing categories. Detection never establishes that a legal wrong occurred.
The decision contains codes, template references and referral kinds, with no
copy of the query or user facts. Multiple urgent signals are retained.

The wider taxonomy includes employment, land, family, debt, criminal matters
and substantive rights. Every such domain requires a professional even when a
procedural keyword also matches. Examples such as employment documents or land
registration forms cannot bypass that gate. Unknown domains abstain. Procedural
navigation does not establish eligibility, fees, timelines or applicable law.
Any future displayed fee/timeline requires dated verified source evidence.

Forbidden requests include legal conclusions, recommendations, pleading,
signing, litigation strategy, criminal defence and deadline calculation. The
limitation template says time limits may apply and may already have expired,
and calls for an attorney-at-law now. No calculator, legal deadline, individual
recommendation or generated legal explanation is introduced.

## Input and language boundaries

The strict request accepts `text` (1–1024 characters), `language` (`en`, `si`,
`ta`, `si-Latn`) and six strictly boolean `urgent` fields. Unknown fields and
coerced booleans are rejected. T5 must add an HTTP byte limit before JSON parsing.
The gate inspects at most the first 4096 characters for obvious urgency before
schema validation. A recognised urgent signal wins even when other fields are
malformed. Urgency outside that prefix of an oversized request is not scanned;
the oversized request still abstains before any downstream stage.

Rules use NFKC, case-folding, whitespace normalisation and removal of format
characters for matching. ASCII phrase boundaries avoid matching `rape` inside
`grape`. Long multiword urgency seeds also tolerate spacing, punctuation and a
small fixed leet mapping. Known Sinhala, Tamil and Singlish seeds escalate
without invoking a model or transliterator. Quotation, hypothetical framing and
negation do not cancel a matched urgent signal. This intentionally costs false
positives while review is pending.

The rule set is a provisional lexical baseline, with version `1`. It cannot
recognise every paraphrase, spelling, dialect or obfuscation. The tests establish
specific synthetic examples, not population recall or real-world safeguarding
validation. Tamil and explicit Singlish non-urgent navigation abstain until
measured/reviewed coverage exists. Model classification must never override an
earlier deterministic escalation. Keep public navigation disabled until attorney,
safeguarding, language and golden-set review.

## Fixed bilingual copy and review

`src/lai/triage/data/templates.json` contains six fixed message IDs in English
and Sinhala: urgent, refuse, professional, limitation, abstain and extractive.
All 12 are UNREVIEWED drafts. They are authored seed copy, never runtime model
output or a legal gloss. They contain no interpolation placeholders and never
incorporate user facts.

`approved_messages` returns copy only when every selected message has explicit
attorney and language-review dates no later than the request's `as_of`. Missing
approval yields an empty tuple. T5 must treat this as an unavailable product
response and keep the public flow closed. Reading draft files for operator review
does not authorise public display. These metadata checks represent review
assertions; independent review evidence and launch approval are still required.

## Referral evidence and expiry

The version-2 register contains 91 publisher listings checked on 19 November
2026: the Commission head office, 84 regional locations, BASL's general office
and five scoped emergency/support channels. Two specialist urgent routes remain
UNVERIFIED. Pending records cannot contain contact/service details. Regional
phones are withheld because the publisher's map data is ambiguous. See
`referral-verification.md` for exact sources, hashes, conflicts and limits.

`active_referrals` requires an explicit matching urgency to return emergency
records. A complaints channel, mental-health helpline and ambulance service
remain distinct through their channel labels. No police record is automatically
selected for unlawful detention or self-harm. A regional filter matches the
published locality label; it does not establish a legal catchment area.

To activate a record after access is available:

1. Inspect the responsible primary page and the linked official directory.
   Confirm each service/number/address against the actual content; a reachable
   homepage alone verifies none of those details. Avoid personal staff details.
2. Preserve the evidence outside Git and record its SHA-256, exact source URL,
   inspected date and `primary_source_inspection` method. Record contact/service
   scope exactly. Review contradictions before using any field.
3. Set `VERIFIED` and a review due date within at most 90 days. The present
   general/directory listings use 30 days and emergency channels use 14 days.
   These provisional engineering intervals do not guarantee availability.
4. Run `make verify`. `active_referrals` excludes unverified, future and expired
   records and filters requested kinds. It performs no runtime network fetch.
5. Obtain the required attorney/safeguarding and product review before display.

Allowed primary hosts are scoped by referral kind, including the Police, NCPA,
NIMH and Suwa Seriya for emergency/support listings. Regional records bind the
Commission contact page to its linked map export with both content hashes.
No runtime fetch occurs. Actual telephone reachability, individual eligibility
and public-copy approval remain unverified. No institution was contacted.

After explicitly acquiring source artefacts outside Git, run the offline audit:

```sh
uv --cache-dir .local/uv-cache run --frozen --offline python \
  scripts/check_referral_evidence.py --directory data/research/referrals/2026-11-19
```

It verifies stored hashes, source/date bindings, telephone strings, exact regional
addresses and the publisher-to-map link. Human source inspection still determines
service scope and hours; the audit is not a live availability or legal review.

## Executed checks and limits

The T4 follow-up passed 324 offline tests. The 221 safety
tests include all six urgency classes in four language seed groups, adversarial
formatting/override attempts, malformed requests, explicit flags, forbidden
advice, limitation flags, gated domains, downstream exceptions, template review
and referral expiry. Independent spies cover entry, analysis, model and retrieval.
A permitted private path exercises those spies; a separate integration test uses
the real T3 retriever with synthetic sources. All service/hardware tests remain
excluded. See `turn-logs/T4.md` and `turn-logs/T4-referrals.md` for actual commands,
failures and delivery receipts.
