# Working on LAi

This file carries the eight-turn delivery contract. Read it with `DECISIONS.md`,
`NEXT.md`, the latest turn log, and `docs/source-verification.md` before changing
the project. Use British English, readable code and honest evidence. Work as an
engineer. Never present yourself or this software as a lawyer.

## Mission and safety invariants

- Build a Sri Lankan legal information navigator, explicitly non-authoritative.
  Map everyday scenarios to candidate law and procedure, display the actual text
  with citations and connect users to real legal professionals.
- Sinhala-first users and largely English sources. Design language contracts for
  Sinhala, Tamil and English now. Tamil product delivery is a later phase.
- Default v0 covers procedural and administrative navigation, including documents,
  offices, fees, timelines and governing instruments. Any fee or timeline must
  have dated, verified source evidence. Wider employment and substantive-rights
  classes belong in the taxonomy, gated behind escalation until attorney review.
- Retrieval-augmented, citation-anchored and extractive-first. No fine-tuning for
  knowledge. Never use model knowledge as legal evidence.
- Assemble answers from verbatim retrieved provisions, complete citations,
  provenance and a human-reviewed template keyed to the provision and version.
  Without a reviewed gloss, show the text and route to a professional. Never
  improvise an explanation or free-form Sinhala legal prose.
- A small local model may perform only bounded script/language detection,
  transliteration, fixed-taxonomy intent classification, extraction of dates,
  amounts, district and employment status, query rewriting, and constrained
  extractive summaries of retrieved text. Strict schemas, validators and
  deterministic fallbacks must contain its output. Measure Sinhala capability.
- Models must never produce a legal conclusion, deadline or recommendation, or
  advise on pleading, signing, litigation strategy or criminal defence. Do not
  compute limitation deadlines as advice. Hard-flag that time limits may apply
  and may already have expired and that a lawyer should be consulted now.
- Triage and escalation are deterministic code before retrieval. Immediate
  escalation short-circuits the entire analysis/retrieval/model path for domestic
  violence, child protection, sexual violence, unlawful detention, imminent
  destitution and self-harm risk. Test each path, including malformed and
  adversarial input, using spies that prove downstream work never runs.
- Present multiple candidate provisions. A single confident match is unsafe.
  Abstain when enough eligible candidates or evidence are unavailable.
- Every displayed provision carries instrument type, number, year, section,
  language version, source URL, retrieval date, amendment status, commencement
  status and a staleness warning. Record content hashes and source revisions.
- Never invent citations, sections, cases or hotline numbers. Record uncertainty
  as UNVERIFIED in the relevant register and in `NEXT.md`.

## Hardware, money and privacy boundaries

- TARGET A is the cloud container. Deterministic parsers, provenance graph,
  triage rules, assembly, API, templates and CI must be testable without GPU or
  network, through fake/stub adapters and tiny synthetic fixtures.
- TARGET B is the maintainer's Xubuntu laptop with 16 GB RAM, a 4 GB GPU and a
  1 TB SSD. Embeddings, inference, OCR at scale, full ingestion and integration
  measurement run there. Deliver interfaces, fakes and junior-friendly scripts.
- Mark hardware/service/network tests `local`, `gpu` or `network`. Exclude all
  three from CI. Never hide deterministic checks behind those markers.
- The 8 GB home-lab server runs real services. It is off limits for deployment or
  writes. Do not connect to it for this project. Production SaaS systems and live
  data are off limits. Only dedicated development stacks with synthetic seeds
  may be changed.
- Default spend is EUR 0, with a EUR 5 monthly ceiling. Use FOSS. No paid APIs in
  the runtime, hosted vector database or commercial LLM in the request path.
- Runtime is offline-first. No user query content may leave the machine or the
  country. Install/download operations are separate from runtime. Test runtime
  egress restrictions in T7 before making isolation claims.
- Basic use has ephemeral sessions and no accounts. Minimise data and define
  retention, deletion, backups and non-identifying observability in T7. Logs must
  never capture queries or identifying facts. No real personal data in code,
  fixtures, logs or tests. All example situations are invented.
- The maintainer is an entry-level DevOps practitioner with no ML experience and
  no qualification to advise. Reuse familiar PostgreSQL, Docker, Caddy, CI and
  Prometheus/Grafana patterns. Prefer modest, documented work that fits alongside
  ongoing study and weekly publishing. Clear history and docs are deliverables.

## Corpus and evidence

- Inventory the maintainer's legal-document repositories and upstream datasets
  in T2. Discover their actual contents and licences before choosing canonical
  sources. Do not assume the brief's counts or coverage are current.
- `docs/source-verification.md` preserves the brief's starting dataset counts,
  benchmark measurements, PDPA assertions and referral leads. They are research
  inputs, with verification state recorded explicitly.
- Maintain an explicit pre-1981 gap register and manual seeding path. Foundational
  prescription/limitation, criminal, civil procedure, land and labour sources
  have priority. Close coverage gaps for every offered domain before launch.
- Detect unextracted, garbled and legacy-font text, including FM Abhaya and
  DL-Manel. Map only verified conversions, otherwise quarantine. Store a quality
  score and reasons per document and gate retrieval eligibility.
- Preserve source artefacts outside Git. Ingestion must be idempotent, hash-based,
  deduplicated and attributable. Chunk at section boundaries.
- Model instruments, amendments and commencement as a versioned graph. Do not
  imply consolidation, applicability or current force from flat source text.
- Use BGE-M3 directly for cross-lingual retrieval, dense plus sparse. Reranking is
  optional and must fit the laptop. Legal-text recall must be measured separately
  from government service-page benchmarks. Translation is not the default path.
- Reverify perishable legal claims against primary Acts, gazettes and the Data
  Protection Authority. Label verified legal claims with
  `[PERISHABLE: verified YYYY-MM]` only after an actual check. Pending claims carry
  UNVERIFIED, the attempted date, source and blocker. Do not fabricate verification.
- T7 must provide a PDPA-mapped DPIA, DPMP, Schedule V notice, breach runbook and
  questions for qualified counsel. These are compliance skeletons, with advice
  and unsettled legal interpretation referred to counsel.
- T4 must verify current Legal Aid Commission contacts and regional counters
  against `moj.gov.lk` / `legalaid.gov.lk`. Keep referrals and emergency routes as
  versioned data with verification dates. Include the Bar Association route to
  attorney review. Do not ship invented numbers or unverified emergency details.
- T8 includes a one-page partnership approach and a referral handoff that can
  connect to an institutional hotline/intake system. Verify the UNDP programme
  assertion before treating it as an existing integration commitment.

## Stack and repository rules

- Default stack is Python 3.12 with uv, PostgreSQL 16 with pgvector, BGE-M3 via
  FlagEmbedding/ONNX/quantisation, optional bge-reranker-v2-m3, a 4B-class Q4
  instruct model via llama.cpp or Ollama for bounded tasks, Tesseract Sinhala with
  a modern OCR fallback, FastAPI, minimal HTMX or React, Docker Compose,
  Prometheus/Grafana and GitHub Actions. Do not add a second datastore without
  cause. Record any substitution and its one-line justification in `DECISIONS.md`.
- Budget and measure RAM/VRAM, latency and quality. Do not assume all components
  fit concurrently in 4 GB VRAM. Never assume Sinhala model or OCR competence.
- Use pytest, Ruff and strict mypy. `make` must expose `setup`, `lint`, `test`,
  `verify`, `ingest`, `serve` and `eval`. Pending commands fail explicitly.
- CI on every push must run lint, type checks, unit tests, schema validation,
  deterministic safety-rule tests and repository hygiene. Keep `main` green.
- Use small atomic Conventional Commits on `main`. Commit and push each turn and
  create an annotated tag. Never force-push, reset shared history or amend a
  published commit. Use the existing isolated cloud checkout. Do not create a Git
  worktree unless the user explicitly requests one.
- No corpus documents, PDFs, model weights, embeddings, vector stores, databases,
  archives, `.env` files, credentials, tokens or files over 1 MB in Git. No LFS.
  Ignore local data/model paths and fetch external artefacts by explicit scripts.
  Fixtures are tiny and synthetic. Inspect staged content before every commit.
- Preserve existing user changes, use frozen lockfile installs, keep TLS,
  signatures and checksum verification enabled, and never print secrets or dump
  credentials. Check existing variable binding names and native Git auth before
  requesting additional credentials. Never ask for secret values in chat.
- Recommend Apache-2.0 or AGPL-3.0 with the institutional trade-off recorded. T1
  chooses Apache-2.0. Corpus licensing stays separate, with MIT attribution where
  verified. The licence recommendation is engineering context, not legal advice.
- Maintain one ADR per significant choice in `DECISIONS.md` and ordered work in
  `NEXT.md`. A required code change must have appropriate executable checks.

## Eight turns

Each turn ends after executed verification, commits, push and its annotated tag.
T1 begins with a measured environment probe of Python, CPU, RAM, disk, GPU,
network egress, PostgreSQL installation/startup, Git push and available tools.

| Turn | Tag | Required delivery |
| --- | --- | --- |
| T1 | `t1-architecture` | Probe, two-target split, directory scaffold, licence, ignore rules, this file, README quickstart, Makefile, pyproject, CI/Compose skeletons, architecture diagram, ADR-0001, risk and corpus-gap registers, at most 300 words on changes to the brief, first green push |
| T2 | `t2-corpus` | Real repository/upstream inventory report, canonical sources and dedupe, provenance schema, quality/legacy-font quarantine, section Act parser, amendment/commencement graph, ingestion CLI, synthetic tests and CI quality gates |
| T3 | `t3-retrieval` | pgvector schema/migrations, embedding interface and deterministic fake, hybrid ranking, Sinhala/Tamil/English/Singlish handling, section chunks, optional rerank, anchored citations, confidence/abstention, evaluation script, offline tests |
| T4 | `t4-safety` | Deterministic taxonomy/triage, all immediate escalations and forbidden advice, limitation flags, English/Sinhala refusal and abstention templates, verified versioned referrals, adversarial/malformed input tests proving short-circuits |
| T5 | `t5-answers` | Extractive renderer, reviewed-gloss schema with UNREVIEWED seeds, bilingual provenance/staleness, missing-gloss text-and-referral path, FastAPI endpoints, minimal UI and API tests |
| T6 | `t6-model-contract` | Bounded task contracts, strict schemas/prompts/validators, deterministic failure fallbacks, VRAM budget, laptop Sinhala measurement script, fake contract tests, independently executable instructions |
| T7 | `t7-operations` | Laptop-only no-egress Compose, minimisation, ephemeral sessions, retention/deletion, safe logs, executed synthetic PostgreSQL backup/restore evidence, observability, DPIA/DPMP/Schedule V/breach skeletons and counsel questions |
| T8 | `t8-evaluation` | Golden set, red-team suite, measured thresholds and GO/NO-GO gates, HANDOFF.md, ROADMAP.md, partnership note, README polish, visibility recommendation, full green suite and `v0.0.0-prototype` |

T8 red-team coverage includes jailbreaks, urgent distress, false premises, stale
law, missing pre-1981 instruments, legacy-font garbage and low-confidence results.
Do not present synthetic/fake-backend success as evidence of real legal recall.

## Evidence and completion

- Write `docs/turn-logs/TN.md` each turn. State what was built, the exact commands
  actually executed and their real relevant output, passes, failures, deferrals
  and reasons. Keep secrets and personal data out. Mark anything unexecuted or
  inaccessible UNVERIFIED. Never claim unrun tests or remote CI passed.
- If blocked, commit the green work, record remaining work in the log and
  `NEXT.md`, and stop cleanly after useful authorised recovery is exhausted.
- Do not deploy or publish this prototype as part of implementation. Environment
  publication belongs to the product/user. Git pushes are authorised by this
  contract. Visibility changes and contacting institutions require user direction.
- Keep the repository private until the launch gate passes, and explain this
  recommendation. Do not assume current repository visibility without evidence.
- **No public deployment to real users until an attorney-at-law has reviewed the
  taxonomy, gloss library and escalation rules, the DPIA is complete, golden-set
  thresholds pass, the corpus gap register is closed for every domain offered,
  and either an institutional partner is engaged or the service is free, clearly
  non-authoritative and referral-first. Private prototype until then.** State
  this plainly in T1, T8 and the README.
- Use engineering judgement and document objections to any harmful constraint
  in `DECISIONS.md`. Never silently drop a rule. Keep T1's changes explanation
  within 300 words. Avoid motivational filler and emoji.
- The final chat response contains only the delivery manifest, with real values
  and commands, in this format.

```text
MANIFEST | turn=N | tag=tN-... | commits=N | CI=pass/fail | verified=[commands run] | next=...
```
