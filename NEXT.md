# Ordered remaining work

## T1 completion evidence

Local verification passed with 33 tests, PostgreSQL 16/pgvector started, the
first commit was pushed to `main` and its GitHub Actions run passed. See
`docs/turn-logs/T1.md` for executed commands and the annotated `t1-architecture`
tag for the final commit's delivery receipt. The next implementation turn is T2.

## T2 — Corpus pipeline

1. Inventory the maintainer's actual document repositories and upstream datasets
   through authorised read access. Verify counts, dates, schemas, hashes,
   canonical sources and licence evidence. Do not download the full corpus into
   this container. Report actual inspected samples with personal data excluded.
2. Implement provenance schemas, content-hash dedupe, idempotent ingestion and
   section-boundary parsing against tiny synthetic fixtures.
3. Implement quality scores, empty/garbled OCR and legacy-font detection, verified
   conversion interfaces and quarantine. Gate retrieval eligibility.
4. Implement the amendment/commencement graph with uncertain states and temporal
   evidence. Add a manual pre-1981 seeding path and coverage closure rules.

## T3 — Retrieval

1. Add PostgreSQL/pgvector schema and migrations plus marked integration tests.
2. Implement fake and real embedding interfaces, dense/sparse hybrid ranking,
   Sinhala/Tamil/English/Singlish handling and section-aware candidates.
3. Anchor citations and enforce several eligible candidates, version checks,
   confidence thresholds and abstention. Add measurement scripts. Measure legal
   recall on TARGET B and qualify provisional thresholds.

## T4 — Safety spine

1. Ship the wider taxonomy and deterministic pre-retrieval triage. Prove all six
   urgent classes short-circuit retrieval and model calls, including malformed
   and adversarial input. Add forbidden advice and limitation-period flags.
2. Create English/Sinhala refusal and abstention templates with review states.
3. Verify Legal Aid Commission, regional counters and emergency routes against
   primary sources. Build versioned referral data and the Bar Association review
   route. Current contacts and numbers are UNVERIFIED and are absent from T1.

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
