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

## ADR-0005 — Immutable intake staging before PostgreSQL indexing

Accepted on 18 November 2026.

T2 stages raw bytes, unmodified UTF-8 extraction, acquisition records and derived
graphs in ignored files. PostgreSQL/pgvector indexing remains T3. These files are
ingestion artefacts with no query index or additional database service.

Verify expected raw/text SHA-256 before side effects. Write blobs through
temporary files, fsync and atomic no-overwrite links, then publish the acquisition
record last. A retry reuses matching files and rejects conflicting contents.
Tests exercise concurrent writers, an interrupted record commit and corruption.

Acquisition records preserve each source/revision/date observation. Version-node
identity uses content, instrument, language and section anchors. Reacquiring the
same content through a mirror retains the version identity. Canonical selection
requires equivalent raw/text hashes, language and complete instrument metadata,
then prefers eligible, reviewed official sources and uses deterministic ties.
Conflicting identities require investigation. No fuzzy merging is performed.

Hashes establish byte integrity. Extraction fidelity and source authority still
need review. Future changes to canonical record serialisation or policy require
an explicit version and compatibility strategy for published records.

## ADR-0006 — Conservative quality and section eligibility

Accepted on 18 November 2026.

Use documented heuristics for empty/short extraction, script mismatch, replacement
characters, private-use glyphs, control characters, mojibake, repeated letters and
known legacy fonts. The score is an engineering gate whose accuracy still needs
human-labelled measurement. Every issue quarantines the document.

Real samples exposed two defects before delivery. A long underscore divider
triggered repeated-letter detection, and combining marks depressed readability.
The policy now checks repeated alphabetic glyphs and excludes combining marks
from the readability denominator. Synthetic regression tests cover both.

English Acts and ordinances support exact section spans, subsections and inserted
section labels. Duplicate, missing or unordered headings, schedules and unsupported
languages/instrument types remain quarantined. Sinhala/Tamil quality measurement
works now. Their section parsers and verified legacy-font conversions require
further work. No conversion mapping is guessed.

## ADR-0007 — Explicit version evidence and source selection

Accepted on 18 November 2026.

Store manually evidenced amends, repeals, commences and supersedes edges. Validate
endpoints, source spans, hashes and same-provision supersession, and reject
supersession cycles. Status inspection revalidates evidence. Only reviewed,
readable-source edges with known effective dates reached at the requested date
contribute recorded status. Every result retains `coverage_unverified`.

The graph never automatically edits statutory text or creates a consolidated
edition. A typed `reviewed` flag records an operator assertion whose supporting
human review remains a launch prerequisite. No legal relationship was inferred
from the real research samples.

The observed index is `nuuuwan/lk_datasets`, and its Acts source is
`nuuuwan/lk_legal_docs` on a dedicated data branch. The separate Parliament Acts
pipeline offers older material with different extraction coverage. Prefer the
original official publisher when verified, retain pinned mirrors as acquisitions,
and use the older pipeline as supplementary gap research. Primary-source checks,
PDF rights and the maintainer's unidentified corpora remain UNVERIFIED.

## ADR-0008 — Scope runtime-directory ignores to the checkout root

Accepted on 18 November 2026.

T1's unanchored `corpus/` ignore also hid `src/lai/corpus/`. Anchor runtime data
directories to the checkout root and align the file guard with that scope.
Corpus documents remain forbidden in Git. A regression test permits source
modules while rejecting a root corpus artefact. Wheel inspection also confirms
that the intake modules are packaged and runtime corpus artefacts are excluded.

## ADR-0009 — Exact cosine and sparse token-weight ranking

Accepted on 18 November 2026.

Use PostgreSQL 16/pgvector `vector(1024)` for dense vectors and JSONB sparse
token weights with a GIN key index. BGE-M3's documented dense dimension is 1024
and its input context is 8192 tokens. Native sparse weights and dense cosine
produce independent top-15 lists, fused with reciprocal-rank constant 60.

Start with exact cosine ranking so approximate-index recall introduces no
additional calibration variable. ANN indexing and reranking require measured
benefit, memory and legal recall. Reranking remains optional and deferred.
The deterministic fake has a configuration-specific identity and accepts only
synthetic sources. Collections reject incompatible model identities/dimensions.

## ADR-0010 — Source and version checks before candidate publication

Accepted on 18 November 2026.

Whole-section chunks reuse T2 graph node identities and preserve the original
UTF-8 extraction. Every result revalidates its acquisition, source bytes, section
span/hash and scoped document/provision graph evidence. Known amendment, repeal
or supersession evidence excludes affected text pending review. Every displayed
candidate carries complete provenance and legal-currency warnings.

Synthetic and real source scopes are explicit. Retrieval defaults disabled.
The private research interface returns at least two distinct logical provisions
or abstains. Language versions and mirror acquisitions cannot inflate that count.
The HTTP API exposes health while T4 triage and T5 assembly are pending.

Active source selection is explicit. Equivalent acquisitions use T2 canonical
selection, while conflicting versions of the same instrument/language require
operator selection before batch updates. Replacing a document is transactional,
retains acquisition history and removes its old chunks when it becomes
quarantined. A single SQL statement obtains both ranking channels from one
database snapshot. Tests exercise rollback, retry and separate concurrent writers.

## ADR-0011 — Separate the lightweight environment and local model profile

Accepted on 18 November 2026.

Keep default installation and CI free of model inference dependencies. Declare
the optional frozen `models` extra with FlagEmbedding 1.4.2, observed in PyPI
metadata, and CPU PyTorch wheels for Linux x86-64. Other platforms retain their
resolved platform-specific packages. Model profile installation and inference
were not executed in this container and remain UNVERIFIED.

The local adapter consumes a caller-selected model directory/revision, sets
offline library flags and disables remote model code. It checks token counts
before encoding to prevent silent truncation and requests dense/sparse output
with batch size one. The explicit acquisition helper pins the resolved model
revision, checks supplied publisher LFS hashes, retains notices and writes a
stream-verified checksum manifest. Real SDK inference and capacity belong to
TARGET B. No legal-quality claim follows from adapter contract tests.

## ADR-0012 — Private local database connections and credential-safe errors

Accepted on 18 November 2026.

The managed rootless Docker daemon reported no published TCP mapping for the
internal database network. A preserved-volume recreation reproduced that result.
Bind the PostgreSQL Unix socket inside owner-only `.local/` and let the local
driver prefer it. Loopback TCP remains a supported connector route when present.
The database stays attached to its internal network.

The first failed TCP connection's test traceback exposed the generated local
development password. That credential was rotated immediately through the local
database role and ignored password file. The connector now uses a temporary
mode-0600 libpq passfile, keeps its contents out of driver arguments, deletes it
after connection and emits a fixed error on failure. Regression tests check
argument/traceback redaction and fresh-setup private directory permissions.

This recovery concerns the dedicated synthetic development stack. Production
systems were not accessed. The T7 full logging/privacy review remains required.

## ADR-0013 — Provisional thresholds and measured synthetic evaluation

Accepted on 18 November 2026.

Default policy uses a provisional dense floor of 0.5, two minimum candidates,
five displayed candidates and a pool of 15. The explicit synthetic demonstration
uses a 0.05 floor for feature-hash vectors. Ranking scores remain raw scores with
an unvalidated-threshold warning. No probability of legal correctness is emitted.

Evaluation reports Recall@1/5/15, mean reciprocal rank and abstention rate with
dataset/backend identity. Five invented queries exercise English, Sinhala, Tamil
and a bounded Singlish lookup. Unknown explicit Singlish abstains. Latin script
alone does not determine language. Actual cross-lingual legal recall, translation
coverage and threshold calibration remain UNVERIFIED until TARGET B/T8 review.

## ADR-0014 — Deterministic gate before the entire downstream path

Accepted on 18 November 2026.

Introduce `SafetyNavigator` with closed defaults. Urgency precedes request
validation so a known flag or bounded text signal still escalates when another
field is malformed. All other invalid input abstains before analysis, models or
retrieval. Advice requests, limitation questions and substantive domains cannot
enter procedural navigation. Limitation results carry a mandatory fixed warning,
with no deadline calculation. Future product endpoints must use this gate.

Use a provisional versioned lexical baseline with Sinhala/Tamil/Singlish seeds,
Unicode normalisation and limited obfuscation handling. Quotation/negation never
suppresses a matched urgent signal. This accepts false positives while measured
coverage and safeguarding review remain absent. No claim of exhaustive detection
or real-world safety follows from the synthetic tests. Keep navigation disabled.

## ADR-0015 — Review-gated fixed bilingual safety copy

Accepted on 18 November 2026.

Ship six fixed safety messages in English and Sinhala as UNREVIEWED seeds.
No query interpolation or runtime model-generated safety/legal prose is allowed.
Only complete, dated attorney and language approvals enable the selected copy;
missing or future approval suppresses the entire selected message set. T5 must
treat unavailable reviewed copy as a closed product flow. Review metadata records
assertions and does not replace independent review or the launch gate.

## ADR-0016 — Withhold referral details until primary-source verification

Accepted on 18 November 2026.

Official Ministry, Legal Aid Commission and Bar Association HTTPS requests were
blocked by destination policy. The user approved six specific host grants; the
network-only draft was saved without changing scripts, repository membership,
credentials or publication. The observed running policy still lacks the grants.
Saving a draft does not establish applied access or content verification.

Record pending targets, dates and blockers, with no numbers, addresses, hours,
regional claims or service promises. Runtime selectors exclude unverified,
future and expired records. Verified entries require a primary-source digest,
inspection date, method and review due date within 90 days; that interval is a
provisional engineering maximum. Current contacts, regional counters, emergency
routes and the attorney-review route remain explicitly UNVERIFIED. This external
T4 work must resume after settings application; it is not completed by schema tests.

## ADR-0017 — Publisher-bound listings and scoped emergency selection

Accepted on 19 November 2026; follows ADR-0016's resolved access prerequisite.

Use the responsible publisher's inspected page for contact fields. The Commission
contact page governs over conflicting older Ministry contacts. Preserve the
Commission-to-map authority link and both hashes for regional locations. Withhold
regional phones because scientific-notation fields and a head-office fax mismatch
do not establish trustworthy telephone contacts. The linked blank PDF supplies no
usable directory evidence. BASL remains a general-office enquiry route with no
inferred review/referral programme commitment.

Version 2 adds channels, cautions, extra published phones, directory evidence and
urgent categories. Emergency selection requires a matching urgency; complaints,
support and medical response remain distinct. No police channel is automatically
selected for detention or self-harm. Keep two specialist urgent routes pending.
Listing checks establish published metadata, not availability, safeguarding
suitability, representation or display approval. Use provisional 30-day general
and 14-day emergency rechecks within the existing 90-day maximum. Raw artefacts
remain outside Git; byte/field auditing is separate from manual scope inspection.

Use the user's corpus links alongside T2, deduplicating the repeated URL. Verified
official publishers govern conflicts; retain mirror provenance and investigate
different versions rather than silently consolidating them. Reviewer availability
does not set approval flags. Provide a concrete reviewer handoff.

## ADR-0018 — Revalidate sources and bind reviewed gloss text/version

Accepted on 19 November 2026.

Pass through T4 before downstream work, then recheck every selected section
against CAS and scoped version evidence before display. Any invalid selected
source closes the answer. Multiple distinct provisions remain mandatory. No new
conclusion, fee, timeline, deadline or translation is generated. Missing glosses
retain original text with the reviewed professional-referral message and current
scoped contact listings.

Bind gloss review to acquisition/chunk, source revision/language/section hash,
display language, review dates/evidence reference and reviewed-text SHA-256.
Changed versions/languages or edited gloss text cannot reuse approval. Four
synthetic seeds remain UNREVIEWED. Metadata records assertions; actual reviewer
evidence and the complete launch gate remain required.

## ADR-0019 — Closed local UI and bounded ephemeral API

Accepted on 19 November 2026.

Use FastAPI with local HTML/CSS/vanilla JavaScript for the single-form interface;
this substitutes for HTMX/React to avoid a frontend build/runtime dependency.
Default to Sinhala, preserve quotes with textContent and retain full bilingual
provenance/currency warnings. Clear aborts pending responses. Queries use POST
bodies and no browser storage, URLs or cookies.

Default copy is unreviewed and navigation disabled. Injected synthetic fixtures
test the approved path without approving shipped copy. JSON is bounded to
16 KiB/16 nesting levels, duplicate keys rejected, errors redacted, hosts/origins
restricted and responses uncached with a restrictive CSP. These checks do not
establish T7's full logging/retention/no-egress guarantees. The separate offline
review packet is explicitly synthetic/UNREVIEWED and opens no product flow.

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
