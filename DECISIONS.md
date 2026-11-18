# Architecture decisions

## ADR-0001 — Extractive assembly and deterministic escalation

Accepted on 18 November 2026.

The corrected approach separates source evidence from language-model behaviour.
LAi retrieves several section-level candidates, checks their provenance and
version state, then assembles verbatim text with a reviewed, version-bound gloss.
Deterministic triage precedes all retrieval and model work. Absent reviewed
glosses, the renderer shows source text and offers a professional referral.

Knowledge fine-tuning and free-form legal answers cannot preserve citation,
version and explanation review boundaries. The bounded local model handles
strictly enumerated language and query tasks. Unusable model output triggers
deterministic fallback or abstention. Administrative navigation is the initial
scope. Wider risky classes require escalation and attorney-reviewed expansion.

This costs coverage and convenience while review and source gaps remain open.
That constraint is represented as data and tested gates. No domain is currently
offered to users. Evidence comes from future legal-text evaluation and attorney
review, separately from software tests.

## ADR-0002 — Two targets and one datastore

Accepted on 18 November 2026.

Retain Python 3.12, uv, PostgreSQL 16/pgvector and FastAPI. Use Docker for the
optional development database because a working Docker daemon is present and
host PostgreSQL binaries are absent. This is a packaging choice within the
default stack. No extra datastore is introduced. The Makefile defaults uv's cache
to ignored `.local/uv-cache` because the managed home directory is read-only.
An explicit `UV_CACHE_DIR` override is preserved.

TARGET A tests all deterministic behaviour with fakes and no Internet sockets,
GPU or database. TARGET B measures BGE-M3, bounded 4B Q4 inference, OCR and full
corpus ingestion on the 16 GB/4 GB laptop. Hardware-dependent tests are explicitly
marked and excluded from CI. Model/OCR backends remain provisional until laptop
measurements prove capacity and language quality. Heavy downloads are deferred.

## ADR-0003 — Apache-2.0 implementation licensing

Accepted on 18 November 2026.

Choose Apache-2.0 to permit institutional reuse with familiar attribution and
patent terms. AGPL-3.0 offers a network-service source-sharing obligation that
could protect contributions but can complicate institutional procurement.
This records an engineering preference, subject to qualified licence review.
The upstream corpus retains its independently verified licence and attribution.
No corpus is bundled. The standard licence text is obtained from SPDX.

## ADR-0004 — Explicit evidence and closed release defaults

Accepted on 18 November 2026.

The brief's corpus counts, benchmark, PDPA dates and referral leads are starting
claims. They become verified only after primary-source inspection, with source
and date recorded. A blocked request leaves the claim UNVERIFIED. Synthetic
unit tests never establish corpus recall or legal validity. No referral numbers,
legal citations or Sinhala legal glosses are invented to complete a scaffold.

The public release contract uses strict booleans with defaults closed. Every
review/measurement condition is required plus the brief's institutional or free
referral-first delivery condition. Release evidence needs independent review.
A true flag alone does not establish the underlying event occurred.

## Changes from the brief

The repository already has an initial README commit, so preserve that history.
PostgreSQL is probed through Docker instead of installing host packages because
the managed daemon already works. The T1 API exposes only health, and the first
safety tests cover release prerequisites. Full request triage remains T4.

Treat every perishable starting claim as UNVERIFIED until a source check succeeds,
including the brief's future-dated legal and benchmark assertions. This prevents
unearned verification labels. Corpus inventory and contact verification remain
their scheduled T2/T4 tasks.

Choose Apache-2.0 for institutional reuse. Retain the default stack and procedural
scope. Exclude model weights, real corpus downloads and inference from T1 so the
container establishes a reproducible, deterministic foundation first.

The launch gate and professional review requirements retain their full force.
The eight turns are separate deliveries. This turn completes T1 and records
subsequent work in order.
