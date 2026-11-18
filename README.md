# LAi

LAi is a Sinhala-first, non-authoritative navigator for Sri Lankan legal information.
It will present several relevant provisions with their sources and connect people to
legal professionals. It never provides legal advice.

**Private prototype. No public deployment to real users until an attorney-at-law has
reviewed the taxonomy, gloss library and escalation rules, the DPIA is complete,
golden-set thresholds pass, the corpus gap register is closed for every domain
offered, and either an institutional partner is engaged or the service is free,
clearly non-authoritative and referral-first.**

T1 provides the architecture, development checks and a health endpoint. Search,
legal answers, ingestion, models and a user interface are pending. Every release
gate starts closed. GitHub's repository page reported the repository as public
during T1. Recommend making it private until the T8 gate passes, because unfinished
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
repository hygiene
and tests with Internet sockets disabled. After installation, verification uses
no network, GPU, database or model. `serve` binds to `127.0.0.1:8000` and disables
access logs. `GET /health` reports `navigator_enabled: false`.

For the optional synthetic development database, install Docker with Compose v2.
This creates a dedicated local volume, never a production connection.

```sh
docker compose config --quiet
docker compose up -d --wait db
docker compose exec -T db psql -U lai -d lai -v ON_ERROR_STOP=1 \
  -c 'SELECT version();'
docker compose stop db
```

The database binds to loopback port 54329 and an internal Docker network. Runtime
egress testing and the full laptop application arrive in T7. Image pulls and
dependency installation need network access. Live processes are restarted after
restoring a cloud snapshot.

| Command | Current behaviour |
| --- | --- |
| `make setup` | Frozen dependency installation and ignored local configuration |
| `make lint` | Ruff lint and formatting checks |
| `make test` | Deterministic unit and safety tests |
| `make verify` | All required T1 checks |
| `make ingest` | Explicitly unavailable until T2, exits unsuccessfully |
| `make serve` | Local health endpoint |
| `make eval` | Explicitly unavailable until T8, exits unsuccessfully |

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
Legal claims, phone numbers and corpus coverage supplied in the brief remain
unverified until primary-source checks are recorded.

- Read [the architecture](docs/architecture.md), [decisions](DECISIONS.md) and
  [contributor rules](AGENTS.md).
- Follow [the remaining work](NEXT.md), [risk register](docs/risk-register.md) and
  [corpus gaps](docs/corpus-gaps.md).
- Inspect [the T1 evidence](docs/turn-logs/T1.md) and
  [source verification register](docs/source-verification.md).

The implementation uses Apache-2.0 for straightforward institutional reuse.
AGPL-3.0 would require corresponding source for modified network services, which
may protect public contributions while complicating some institutional adoption.
Upstream corpus licensing and attribution are assessed separately during T2.
No corpus, model, database, credentials or personal data belongs in Git.
