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
