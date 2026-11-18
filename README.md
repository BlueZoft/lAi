# LAi

LAi is a Sinhala-first, non-authoritative navigator for Sri Lankan legal information.
It will present several relevant provisions with their sources and connect people to
legal professionals. It never provides legal advice.

**Private prototype. No public deployment to real users until an attorney-at-law has
reviewed the taxonomy, gloss library and escalation rules, the DPIA is complete,
golden-set thresholds pass, the corpus gap register is closed for every domain
offered, and either an institutional partner is engaged or the service is free,
clearly non-authoritative and referral-first.**

T8 adds synthetic acceptance, a review-bound legal golden-set schema and handoff.
**Public use is NO-GO**; reviewed legal labels and calibrated thresholds remain
unavailable. See [HANDOFF.md](HANDOFF.md), [ROADMAP.md](ROADMAP.md) and
[review instructions](docs/evaluation.md). Prototype tags authorise no deployment.

T7 provides a standalone Unix-socket runtime with no container networking, tested
synthetic encrypted backup/restore, content-free logs/metrics and scoped retention.
PDPA primary texts were inspected; governance/notice documents remain unapproved
counsel-review drafts. T6's bounded model research stays separate. T5's extractive
answers and Sinhala-first interface still use T4 safety routing. The default query interface
remains closed pending review. Bilingual safety copy is
UNREVIEWED. The referral register now contains 91 checked publisher listings,
including 84 regional locations. Ambiguous regional phone fields and two
specialist urgent routes remain withheld. Listing verification does not establish
live availability or approve public display. Actual model quality and legal recall
remain UNVERIFIED. Every release
gate starts closed. GitHub’s API reports public visibility on 19 November 2026.
Recommend making it private until the full gate passes, because unfinished
legal material can be mistaken for a usable service.

## Quickstart

Use Python 3.12 and [uv](https://docs.astral.sh/uv/). Run in the existing checkout.
Cloud tasks are already isolated, so use that checkout directly.

```sh
make setup
make verify
make serve
```

`setup` installs the locked dependencies and creates an ignored, random local
database password. The default uv cache lives under ignored `.local/`, which
works with the cloud container's read-only home directory. An existing
`UV_CACHE_DIR` setting takes precedence. `verify` runs lint, types, schema checks,
repository hygiene and tests with Internet sockets disabled. After installation, verification uses
no network, GPU, database or model. `serve` binds to `127.0.0.1:8000` with a fixed
content-free formatter and no access logs. This host development command does
not prove network isolation. `GET /health` reports `navigator_enabled: false`.

For the optional synthetic development database, install Docker with Compose v2.
This creates a dedicated local volume, never a production connection.

```sh
docker compose config --quiet
docker compose up -d --wait db
docker compose exec -T db psql -U lai -d lai -v ON_ERROR_STOP=1 \
  -c 'SELECT version();'
docker compose stop db
```

The local driver uses a private Unix socket under `.local/postgres-socket` when
available. This supports the cloud's rootless internal network, whose configured
loopback port is not published by the daemon. The connector also supports loopback
port 54329 when available. The separate T7 runtime uses no networking and Unix
sockets; its cloud proof does not establish whole-laptop isolation. Image pulls and
dependency installation need network access. Live processes are restarted after
restoring a cloud snapshot.

| Command | Current behaviour |
| --- | --- |
| `make setup` | Frozen dependency installation and ignored local configuration |
| `make lint` | Ruff lint and formatting checks |
| `make test` | Deterministic unit and safety tests |
| `make safety` | Deterministic safety, escalation and downstream short-circuit tests |
| `make verify` | Lint, types, schemas, file guard and offline tests |
| `make ingest` | Stage the tiny synthetic Act fixture into ignored `data/corpus/` |
| `make serve` | Private UI, health and default-closed answer API |
| `make review-packet` | Offline synthetic HTML packet; all copy remains UNREVIEWED |
| `make acceptance` | Synthetic acceptance and NO-GO report; no legal approval |
| `make eval` | Aggregate fake-backend measurements on five tiny synthetic queries |
| `make model-demo` | Replay invented model-task labels into a private aggregate report; no inference |
| `make ops-build` | Explicit locked wheel download, then offline Docker image build |
| `make ops-check` | Fresh synthetic network/HTTP/encrypted backup/restore drill; own project cleaned up |
| `make test-local` | Five PostgreSQL tests in a disposable synthetic database |

## Two targets

**TARGET A, this container** develops and tests deterministic parsers, the
provenance graph, rules, answer assembly, API, templates and CI. Fakes and tiny
synthetic fixtures keep these tests independent of hardware and external services.

**TARGET B, the laptop** is Xubuntu with 16 GB RAM, a 4 GB GPU and a 1 TB SSD.
Embeddings, bounded local inference, OCR at scale, full ingestion and integration
measurements run there. Tests marked `local`, `gpu` or `network` are excluded from
CI. No laptop hardware measurement has been performed here.

## Design and delivery

Answers will combine verbatim provisions, complete citations, provenance and
human-reviewed glosses. Without a reviewed gloss, the system will show the source
text and offer a professional referral. Deterministic triage runs first and can
stop retrieval. Model output never decides escalation or generates legal advice.

Start with administrative navigation. Dangerous matters require escalation.
Legal applicability and remaining contact gaps need primary evidence and review. The
inventory records observed upstream counts and extraction limits. The supplied
Supreme Court, Appeal Court and Acts repository links are reconciled with T2;
verified official publishers govern conflicts. See the referral report for the
remaining source and reviewer tasks.

- Read [the architecture](docs/architecture.md), [decisions](DECISIONS.md) and
  [contributor rules](AGENTS.md).
- Follow [the remaining work](NEXT.md), [risk register](docs/risk-register.md) and
  [corpus gaps](docs/corpus-gaps.md).
- Inspect [the corpus inventory](docs/corpus-inventory.md),
  [intake guide](docs/corpus-intake.md), [retrieval guide](docs/retrieval.md),
  [safety guide](docs/safety.md), [T4 evidence](docs/turn-logs/T4.md),
  [referral verification](docs/referral-verification.md) and
  [source verification register](docs/source-verification.md).
- Use [the answer/API guide](docs/answers.md) and [reviewer handoff](docs/reviewer-handoff.md).
  `make review-packet` writes `.local/t5-review.html`; reading it changes no approvals.
- Follow [the bounded model and laptop guide](docs/model-contract.md) for strict
  task contracts, CPU defaults, optional GPU probing and sequential measurements.
  No model output is connected to the answer API; quality and capacity remain UNVERIFIED.
- Use [the private operations runbook](docs/operations.md) and
  [PDPA source evidence](docs/pdpa-verification.md). The [DPIA](docs/dpia.md),
  [DPMP](docs/dpmp.md), [notice](docs/privacy-notice.md) and
  [breach runbook](docs/breach-runbook.md) are incomplete drafts. Controller/bases,
  actual reviews, laptop gateway/OS controls and launch approval remain pending.

The implementation uses Apache-2.0 for straightforward institutional reuse.
AGPL-3.0 would require corresponding source for modified network services, which
may protect public contributions while complicating some institutional adoption.
Upstream code repositories declare MIT. Preserve their notices for material
covered by that licence. Original government PDF rights await publisher review.
No corpus, model, database, credentials or personal data belongs in Git.
