# T8 acceptance and golden-set review instructions

19 November 2026. **NO-GO for public use.** The user confirms that a reviewed
legal golden set does not yet exist and requests instructions. This delivery
provides synthetic acceptance checks and a review-bound data format, not invented
legal measurements. Reviewer availability does not substitute for actual review.

## Reproduce the engineering report

```sh
make setup
make verify
make safety
make acceptance
```

`acceptance` emits aggregate JSON without scenarios, runs 12 invented adverse
triage cases with spies and the five-query fake retrieval experiment, and reports
NO-GO. It returns failure for a red-team mismatch; a successful command means
engineering checks ran, not that public launch passed. It has no switch to set
independent legal evidence true and never edits launch configuration. Safety
tests additionally exercise stale amendments/repeals, legacy-font quarantine,
missing sources, citation tampering, low similarity, source corruption, jailbreaks,
all six urgency classes and malformed/obfuscated requests. See the test mapping.

| Threat | Executable evidence |
| --- | --- |
| Jailbreak and false premise | `tests/test_evaluation_acceptance.py`, `tests/test_triage.py`; the guaranteed-win form now refuses before downstream work |
| Urgent distress | T4 multilingual/obfuscated/malformed spies and T6 model bypass tests |
| Stale law | `tests/test_retrieval_versions.py`: document-level amends/repeals/supersedes exclude all sections |
| Missing foundational/pre-1981 coverage | Empty/unavailable source paths abstain; the real gap register remains open, not repaired by a fixture |
| Legacy-font garbage | `tests/test_text_quality.py`: legacy-font/private-use/replacement quarantine |
| Low-confidence/single candidate | `tests/test_retrieval.py`: low similarity and fewer than two provisions abstain |
| Changed quote/citation/gloss | `tests/test_answers.py`, source/citation/approval hash binding |
| Retention/egress/logging | T7 unit tests and separately executed synthetic operations drill; host/laptop controls remain unverified |

## Build the real reviewed retrieval set outside Git

1. Select only intended offered domains. Use the T2 inventory plus the supplied
   Supreme Court/Appeal Court/Acts links; verified official sources govern any
   conflict. Resolve rights, source bytes, language quality, version/commencement
   and foundational gaps before treating a source as eligible evidence.
2. Create invented non-personal scenarios in Sinhala and English, with mixed
   script/Singlish/dialects assessed separately. Tamil remains a later product
   phase. Never copy client facts, case-party names or personal identifiers.
3. An attorney labels all relevant section-version chunk IDs against the pinned
   corpus, with source URL/revision/hash and relevance reasoning retained in a
   private review ledger. Include competing provisions and inapplicable near
   matches, not just a single convenient answer. A language reviewer checks the
   scenario meaning independently. Reviewers resolve disagreements explicitly.
4. Put eligible retrieval-positive cases in the existing `EvaluationDataset`
   format (`kind: legal`). Store urgent/refused/unsupported/false-premise/no-source
   scenarios separately with expected action, limitation flag, expected no-call
   behaviour and rationale. They must not be forced to carry a relevant provision
   merely to satisfy the retrieval-positive schema. Keep this safety ledger
   separate from recall denominators and measure both false positives/negatives.
5. Partition calibration and held-out sets before tuning. Avoid paraphrase,
   mirror, instrument-version and language-translation leakage between splits;
   group related sources/scenarios. Start planning at least 200 retrieval cases,
   50 per supported language, plus balanced negative/urgency scenarios. Those are
   proposed sampling floors, not a statistically justified or approved benchmark.
6. Wrap the reviewed retrieval dataset in `GoldenSet` using
   `schemas/legal-golden-set.schema.json`: exact normalised dataset SHA-256,
   offered scope, actual attorney/language dates, retained review-evidence
   reference and calibration/held-out split. Compute the hash from
   `EvaluationDataset.model_dump_json().encode()` using `digest`. Edited datasets
   invalidate the binding. Schema validity records assertions, not actual review.
7. Run the existing `lai-retrieval evaluate-local --help` instructions in
   `retrieval.md` on TARGET B, using pinned real BGE-M3 and source graph/acquisition
   IDs. Retain backend/model/corpus/prompt versions, dataset hashes, date and
   machine resource measurements. No fake model can validate legal recall.
8. Review outputs blindly for source relevance, exact quotes/citations, currency,
   missing sources, abstention and gloss meaning. Record per-domain/language
   counts, uncertainty intervals and all failures, including unsafe non-abstention.
   Re-run untouched held-out data only after calibration decisions are frozen.

## Thresholds and release decisions

The executed fake five-query experiment measures an engineering similarity
threshold of 0.05 only on invented fixtures. It is not a legal threshold. Proposed
review targets are recall@15 >=0.90, recall@5 >=0.80 per supported language/domain,
zero observed urgent downstream calls, zero invented/mismatched citations and
zero unsafe positive answers on known missing/stale/garbled sources. Abstention
and false-positive burdens need reviewer-set targets; measure them separately.
These targets are **UNRATIFIED / UNCALIBRATED**. No claim of legal sufficiency or
statistical confidence follows from meeting a small sample's numeric target.

GO requires independent, dated acceptance of calibrated held-out legal/language
and red-team evidence plus **all** `LaunchGate` review/DPIA/gap conditions and
the institutional or free/non-authoritative/referral-first delivery condition.
Also require verified laptop operations, controller/notice decisions and current
referral safeguards. Any missing, failed, stale or contradictory evidence means
NO-GO. Configuration booleans alone are insufficient; the report cannot approve
its own evidence. A maintainer/counsel review is required before any later
configuration or visibility/deployment decision. No automatic gate flip exists.

Current legal recall, legal golden set, production thresholds, Sinhala model
competence and laptop capacity remain UNVERIFIED. The prototype tag records an
engineering checkpoint with a NO-GO decision, not a public product release.
