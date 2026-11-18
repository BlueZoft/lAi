# Ordered remaining work

## Delivery evidence

Local verification passed with 33 tests, PostgreSQL 16/pgvector started, the
first commit was pushed to `main` and its GitHub Actions run passed. See
`docs/turn-logs/T1.md` for executed commands and the annotated `t1-architecture`
tag for the final commit's delivery receipt.

T2 implements hash-verified intake, provenance schemas, deduplication, quality
quarantine, exact section spans, manual-seed mapping and a version-evidence
graph. The latest local suite passed 96 tests. Read `docs/turn-logs/T2.md` and
the `t2-corpus` annotation for delivery and remote CI evidence.

T3 adds source-anchored hybrid retrieval, deterministic and local BGE-M3 adapters,
PostgreSQL/pgvector migration and indexing, multilingual query handling, strict
multiple-candidate/abstention contracts and aggregate evaluation. The local suite
passes 150 offline tests and five isolated PostgreSQL tests. Read
`docs/turn-logs/T3.md` and the `t3-retrieval` annotation for delivery receipts.

T4 implements deterministic safety routing, all six urgent classes, forbidden
advice/limitation flags, strict contracts, review-gated bilingual copy and an
expiry-gated referral register. Verification passes 318 offline tests, including
215 safety tests. See `docs/turn-logs/T4.md` and the `t4-safety` tag receipt.
Official referral verification remains blocked; the register has no active
contacts. This is an explicit incomplete T4 external prerequisite.

## Source and corpus follow-up

1. Obtain the maintainer's actual legal-document repository URLs. Eleven public
   repository roots/READMEs were inspected, and no corpus was identified there.
   Private/unlisted and nested corpus contents remain UNVERIFIED. A question is
   pending. Add the identified sources to the inventory before selecting them.
2. Inspect official publisher content and original PDF terms when access is
   available. Current requests to `documents.gov.lk` and `huggingface.co` are
   blocked by destination policy. GitHub's API is also blocked, while HTML/raw/Git
   routes work. Full mirror equivalence and rights remain UNVERIFIED.
3. On TARGET B, implement and measure upstream batch adapters, OCR and extraction
   reproducibility. Add verified legacy-font conversion only with source-aligned
   evidence. Sinhala/Tamil structural parsers and schedules remain unsupported.
4. Build a human-labelled text/parsing quality sample set. Close foundational
   gaps only with complete source/version evidence and attorney review. The
   current corpus score is a provisional engineering gate.

## Retrieval measurement follow-up on TARGET B

1. Install the locked optional model profile, acquire a pinned BGE-M3 snapshot
   with the provided helper, and measure RAM, latency and retrieval quality.
   Actual SDK inference, model acquisition and laptop capacity remain UNVERIFIED.
2. Use a human-verified legal dataset to calibrate similarity thresholds and
   measure legal recall. Five synthetic-query measurements establish engineering
   behaviour. Legal recall and launch thresholds remain UNVERIFIED.
3. Supply reviewed Singlish transliteration data or a measured bounded adapter.
   The production default abstains for explicit Singlish without an adapter.
4. Measure oversized-section handling and any future subsection subdivision,
   ONNX/quantisation or reranker. Whole sections above the model's context are
   rejected before encoding. No reranker has been measured.

## T4 external verification and review follow-up

1. Apply the user-approved six-domain network draft in environment settings.
   Draft persistence does not establish live access. Recheck official sources:
   `moj.gov.lk`, `legalaid.gov.lk` and `basl.lk`, plus their `www` forms.
   Initial HTTPS requests were denied by destination policy (CONNECT 403).
2. Verify Legal Aid Commission services, regional counters, emergency routes and
   the Bar Association route to attorney review. Save dated primary-source
   evidence, digest and review expiry in the versioned register before activating
   details. No contact numbers, addresses, hours or service commitments are active.
3. Obtain attorney/safeguarding and Sinhala language review of the taxonomy,
   rules and all 12 fixed templates. All copy remains UNREVIEWED and withheld by
   the approved-message selector. Negation/quotation deliberately does not cancel
   an urgent signal. Measure false negatives and positives on reviewed scenarios.
4. Expand measured language coverage, especially dialects, code-switching, Tamil
   and Singlish. Current multilingual seeds and obfuscation tests establish
   deterministic examples only. Tamil/Singlish non-urgent navigation abstains.

## T5 — Assembly and interface

1. Implement verbatim rendering with complete provenance and staleness warnings.
2. Add version-bound gloss schema and UNREVIEWED synthetic seeds. Only reviewed
   glosses may be displayed. Missing glosses use text and professional referral.
3. Add bounded API endpoints, minimal Sinhala-first UI and API safety tests.

## T6 — Local model contract

1. Ship task specifications, strict JSON schemas, prompts, validators and
   deterministic wrong/unavailable-model fallbacks with fake-based tests.
2. Deliver independently executable Sinhala measurement and RAM/VRAM scripts for
   the laptop, including CPU fallback and sequential residency measurements.

## T7 — Operations and compliance

1. Build and test laptop-only no-egress Compose, ephemeral sessions, minimisation,
   retention/deletion and logs/metrics that cannot capture identifying facts.
2. Execute backup and restore of a synthetic database and preserve real output.
3. Verify all PDPA assertions against primary publications. Produce mapped DPIA,
   DPMP, Schedule V notice and breach skeletons plus questions for counsel.
   Legal status assertions in `docs/source-verification.md` are UNVERIFIED.

## T8 — Evaluation and handoff

1. Build the legal golden set with competent human verification. Run the specified
   red-team classes, measure recall/safety and publish explicit GO/NO-GO gates.
2. Write HANDOFF.md and ROADMAP.md, the one-page partnership approach and a
   verified institutional hotline/intake handoff design. Verify the UNDP lead.
3. Restate the full launch gate and visibility recommendation, run the full suite,
   push the annotated `t8-evaluation` and `v0.0.0-prototype` tags.

## External prerequisites

GitHub's repository page reports Public in T1. Recommend making the repository
private until the launch gate passes. A maintainer must apply that visibility
decision separately from this authorised code delivery.

All attorney reviews, Sinhala review, source-status verification, laptop capacity
measurements, full legal-recall evaluation and institution engagement remain
UNVERIFIED. Keep every public-launch evidence flag closed until supported.
