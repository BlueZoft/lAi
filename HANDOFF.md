# LAi private prototype handoff

19 November 2026. Engineering checkpoint: `t8-evaluation` /
`v0.0.0-prototype`. **NO-GO for public deployment.** No public deployment to real
users until an attorney-at-law has reviewed taxonomy, glosses and escalation,
the DPIA is complete, golden-set thresholds pass, offered-domain corpus gaps are
closed, and either an institutional partner is engaged or the service is free,
clearly non-authoritative and referral-first. Current flags remain false.

## Start and inspect

```sh
make setup
make verify
make safety
make acceptance
make serve
```

The UI is Sinhala-first and default-closed. `serve` is loopback host development,
not a no-egress deployment. Stop it after synthetic inspection. No accounts,
durable queries, free-form legal generation or production integrations exist.
`make review-packet` generates the UNREVIEWED synthetic copy packet.

Read [NEXT.md](NEXT.md), [architecture](docs/architecture.md),
[evaluation/review instructions](docs/evaluation.md) and
[reviewer handoff](docs/reviewer-handoff.md). T1–T8 logs and immutable tags retain
executed evidence and limitations. Use the frozen lockfile; keep real corpora,
weights, private review evidence, credentials and generated reports outside Git.

## What works and what remains

Intake/provenance/quality quarantine, version evidence, source-anchored hybrid
retrieval, deterministic escalation, extractive assembly, reviewed-gloss
contracts, closed UI/API, bounded model research and isolated synthetic operations
are implemented. Source text/version and multiple-provision checks stay mandatory.
All shipped safety/gloss copy remains UNREVIEWED; models are not in the API path.

The user supplies attorney/Sinhala reviewers and corpus URLs; actual review and
legal labels have not been supplied. Review the rules/copy/UI/glosses, safe urgent
routes for detention/destitution, regional phones and current eligibility. Prepare
the reviewed golden set following `docs/evaluation.md`; the user confirms it is
not yet available. Source rights/equivalence, pre-1981 gaps, Supreme Court access,
real recall and actual language/hardware quality remain open.

For TARGET B (16 GB RAM/4 GB GPU), follow [model instructions](docs/model-contract.md)
and [operations](docs/operations.md). Run CPU stages sequentially before optional
GPU probing. `make ops-build` downloads locked wheels explicitly, then builds
offline; `make ops-check` creates/removes only its own synthetic stack and proves
bounded encrypted restore/namespace checks. It does not verify laptop gateway,
BPF, disk/swap, browser, key custody, scheduler or real corpus recovery.

Counsel/operator must assign actual controller/contact, bases, DPO decision,
notice/rights/breach processes and approve DPIA/DPMP. The primary PDPA evidence
is in `docs/pdpa-verification.md`; final instruments/current completeness remain
unresolved. No legal compliance assertion or statutory timer was invented.

## Ownership and next work

Maintainer owns reproducible private engineering. Attorney/language/safeguarding
reviewers own substantive acceptance; qualified counsel/operator own privacy and
release decisions. Keep an evidence ledger with version/hash/date/role/reference,
without personal reviewer details in Git. ROADMAP.md orders the remaining work.
No home-lab/production connection, paid runtime or institution outreach is
authorised by this handoff. Publication/visibility changes require user direction.

Recommend private repository visibility until the full gate passes. The source
is Apache-2.0; corpus/model rights are separate. The one-page partnership approach
is conditional; it creates no LAC/BASL/UNDP commitment or intake connection.
