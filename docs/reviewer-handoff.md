# T4 reviewer handoff

The user reports attorney and Sinhala reviewers are available. This records
availability, not approval. Keep all launch flags closed and all 12 safety
templates UNREVIEWED until the actual reviews are recorded. No reviewer names,
personal contact details or real user situations belong in Git.

| Reviewer task | Concrete material | Decision/evidence needed |
| --- | --- | --- |
| Attorney and safeguarding review | `src/lai/triage/rules.py`, `docs/safety.md`, synthetic `tests/test_triage.py` | Confirm scope, all six escalation classes, forbidden advice, limitation warning and conservative negation handling. Identify missed paraphrases and false positives. |
| Sinhala review with attorney | `src/lai/triage/data/templates.json` | Review each fixed English/Sinhala pair for meaning, safety, clarity and language. Record review dates for that exact revision. Do not improvise legal glosses. |
| Urgent referral policy | `docs/referral-verification.md`, version-2 referral register | Decide safe presentation/alternatives, including where police contact may be unsafe. Establish suitable urgent routes for detention and imminent destitution. Distinguish complaints, mental-health support and medical dispatch. |
| Contact/eligibility review | Commission/BASL sources in the verification report | Confirm current eligibility, opening/access and how a caller can request professional help. Do not infer a BASL review commitment. Resolve regional phones through reliable publisher evidence rather than reconstructing map numbers. |
| Corpus authority/privacy | Updated `docs/corpus-inventory.md` and supplied repository links | Use official publishers to govern conflicts; review original publication rights and judgment-data minimisation. Do not mark mirror/official equivalence without source-byte checks. |

Record the reviewed revision/content hash, dates, reviewer role and a reference
to retained review evidence outside Git. Apply only changes supported by the
actual review, then rerun `make verify` and `make safety`. Template metadata must
have both attorney and language review dates. These assertions do not replace
the wider launch gate, source-gap closure or measured golden-set thresholds.

The unresolved source/access issues are regional telephone ambiguity, the blank
publisher-linked PDF, two specialist urgent routes, and HTTP 403 from the Supreme
Court roots. They do not prevent continued private T5 engineering. They do prevent
claiming complete referral coverage, legal-corpus verification or public readiness.
