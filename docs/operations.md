# Private laptop operations

19 November 2026. Use TARGET B, the maintainer's laptop, for real hardware work.
The cloud executes synthetic development checks only. No public deployment,
environment publication, home-lab/production connection or institution outreach
is authorised. All answer/review/launch defaults remain closed.

## Installation is separate from runtime

Prerequisites: Linux, Python 3.12, uv, Docker/Compose v2 and GnuPG (`gpg` /
`gpgconf`). The base interpreter needs pip for downloading wheels; uv's project
venv need not contain pip. Keep TLS and hash checks enabled. The installed Docker
daemon must be the local intended daemon, never a production context. Check it
without dumping configuration/credentials:

```sh
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS \
  -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock info --format '{{.ServerVersion}}'
make setup
docker --host=unix:///var/run/docker.sock pull python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
docker --host=unix:///var/run/docker.sock pull pgvector/pgvector:pg16@sha256:484e838076e04939d27d3e176e91c86eea96236126023be8d3059761122e579f
make ops-build
```

`ops-build` explicitly downloads wheels against the frozen lockfile/hashes into
ignored `.local/operations-build`, builds the application wheel and builds
`lai-runtime:t7` with Docker build networking disabled. Native/package/image
installation can use network; request-time containers cannot. No registry image
push, model download, paid service or production write occurs. Base image and
PostgreSQL are pinned by digest. The local app tag is intentionally rebuilt from
the local wheel; retain the actual image ID with a test report after changes.

## Execute the synthetic acceptance drill

```sh
make verify
uv --cache-dir .local/uv-cache run --frozen --offline python scripts/validate_runtime.py
make ops-check
```

The drill creates a new random `lai-t7-test-*` Compose project and private scratch
directory. It never starts or changes `lai-dev-db-1`. It checks actual app and DB
namespace network modes, no published ports, disabled Docker logging, app
read-only root and memory cap. Separate tiny probes join each namespace and test
IPv4 TCP/UDP, IPv6 TCP and DNS with invented/reserved destinations. Unix HTTP
checks exercise the real default-closed app and a synthetic private marker.

It creates three invented source/index rows with pgvector, makes a custom-format
dump in RAM, encrypts it with GnuPG AES-256 and integrity protection, rejects a
damaged ciphertext, decrypts in RAM, restores into a fresh database and compares
ordered logical row hashes. Plain dump/key values never enter argv, logs or Git.
The helper is deliberately capped at 16 MiB; it is a synthetic recovery proof,
not a streaming backup implementation for a multi-GB corpus. Future real-corpus
recovery requires scale/rights/key-custody measurements first.

The owned test containers, volume, scratch dumps and generated drill keys are
removed in cleanup. A content-free mode-0600 report remains under
`.local/operations/retained/reports/`. Failed cleanup is a failure, not a successful
drill; inspect only the exact owned project. The app/DB namespaces were tested
in the cloud. Laptop hardware, host gateway/OS/browser controls and real-corpus
recovery remain UNVERIFIED until repeated there.

## Standalone isolated runtime

```sh
make ops-prepare
docker --host=unix:///var/run/docker.sock compose -f compose.runtime.yaml up -d --wait
```

This starts only dedicated local private development containers. It publishes
no port. Both have `network_mode: none`, no external DNS, read-only roots,
resource/PID/core-dump limits and no-new-privileges. The app drops all capabilities
and runs as UID 1000/GID 0; PostgreSQL retains only capabilities needed by its
initialisation entrypoint, then runs its normal dedicated database user. There
are no queries in its persistent source database. The app currently has no
database/model/source wiring and no DB socket/password mount: it remains closed.

The HTTP socket is `.local/operations/api-socket/http.sock`; PostgreSQL's is in
the separate `db-socket` directory. `.local/operations` is 0700, socket directories
0770 and generated credential files 0600. GID 0 lets a rootless container share
the caller's mapped group; verify UID mapping/permissions on the actual laptop.
A rootful daemon with a different host UID may require an operator-reviewed user
override. Do not solve that with world-writable directories or privileged mode.

Use Unix HTTP from the app container for diagnosis:

```sh
docker --host=unix:///var/run/docker.sock compose -f compose.runtime.yaml exec -T app \
  python -m lai.operations.probe http
docker --host=unix:///var/run/docker.sock compose -f compose.runtime.yaml down
```

Normal `down` preserves this dedicated source database volume. Never add `-v` to
that command casually. The acceptance drill deletes only its own fresh test
volume. Inspect a stopped app before removing its stale `http.sock`; the entry
point refuses an existing socket to avoid replacing a live instance. Stop the
owned service first and confirm no listener before deleting that one socket.

## Browser gateway boundary

Browsers cannot speak Unix HTTP directly. `operations/Caddyfile` and
`operations/lai-gateway.service` are **operator-edited templates**, not installed
services. Replace their checkout/user placeholders with the real laptop values.
The Caddy template binds only `127.0.0.1:8000`, disables admin/automatic HTTPS,
has no access log and proxies to the one fixed Unix socket. Plain HTTP here is
loopback-only; this is not a remote/public TLS deployment configuration.

The system service uses `IPAddressDeny=any`, `IPAddressAllow=localhost`, restricted
address families, no core dumps and discarded stdout/stderr. These host BPF/
cgroup controls must actually be supported/enforced, not merely accepted by a
unit parser. A system administrator must install/run the reviewed unit on the
laptop, verify listener/interface scope, successful Unix proxying and failed
external TCP/UDP/DNS before relying on it. No gateway/systemd service was installed
or verified in this cloud turn. Do not run bare Caddy and claim equivalent egress
enforcement. All other host processes/browser extensions remain outside that
container boundary; inspect them separately before real use.

`make serve` remains a loopback **host development** convenience for synthetic
UI work, now with the same content-free formatter. It is not an isolated runtime.
It refuses public host addresses and has no access logs; runtime headers disable
caching/referrers. It must not be represented as proving no-egress.

## Minimisation, retention and deletion

`config/privacy-policy.json` is a strict documented policy: no durable query
history, accounts, cookies or browser storage. The server holds request state in
RAM only; it does not create a session identifier or persist the scenario.
Browser Clear cancels/invalidates responses and clears text/results. Page exit
clears them; back-cache restoration clears again. Five minutes since input or a
completed reply clears the form/results. Browser suspension can delay timers;
leaving/clearing a page does not guarantee Python thread cancellation or secure
heap/OS swap erasure. No byte-level erasure or whole-machine privacy is claimed.

Use encrypted laptop storage/swap or an operator-approved no-swap configuration,
disable sensitive crash/session backups, restrict the laptop account, browser
extensions and screenshots, and keep the screen private. These host controls
are not measured here. Query persistence must not be added to source tables,
support tickets, evaluation fixtures or backups.

Owned reports and encrypted backup artefacts have seven-day retention, using
UTC creation timestamps in their names. Cleanup touches only regular recognised
files under marked `retained/reports` and `retained/backups`; unexpected files or
symlinks stop it before deletion. It never prunes keys, source/provenance data,
the development database or arbitrary `.local` files. Preview then apply:

```sh
uv --cache-dir .local/uv-cache run --frozen --offline python -m lai.operations.retention
uv --cache-dir .local/uv-cache run --frozen --offline python -m lai.operations.retention --apply
```

The laptop operator must schedule daily execution in that owner account and
check its fixed success/failure result. Until scheduled and verified, timed
cleanup is a policy, not an automatic guarantee. T2–T6 research/review files
outside this marked tree need separate manual decisions. Unlink cannot promise
physical SSD/snapshot erasure. Keep recovery keys outside the backup directory,
make a separately protected offline recovery copy and test access; never send
keys in chat. Those actual custody/recovery decisions remain pending.

## Content-free observability

The runtime formatter emits only fixed event codes and info/error severity. It
never formats arbitrary messages, args, exceptions, request extras or traceback
text. Docker logs are disabled for both services; PostgreSQL statement/parameter
logging is disabled. This deliberately reduces diagnostics. Use synthetic
reproduction, health/configuration and counts instead of enabling debug logging.

`GET /metrics` exports a fixed finite set of route groups, status classes and
latency buckets/counts in RAM; it never labels content, paths, IPs, IDs, language,
intent, urgency or facts. Unknown URLs collapse to `other`; counters reset on
restart. Metrics are local operator information, not public telemetry. Even
aggregate low-volume counts/timing can reveal usage; do not share them casually.

Optional native Prometheus can use `operations/prometheus.yml`, loopback only,
with `--storage.tsdb.retention.time=1h`, `--storage.tsdb.retention.size=32MB` and
storage under owner-only `.local/operations/metrics`. Do not configure remote
write/receiver, cloud telemetry, exemplars or extra labels. Optional local Grafana
may visualise request classes/error counts/buckets; disable external analytics
and bind it to loopback. Neither monitoring daemon was installed/run here. Their
configuration, effective retention and gateway boundaries need laptop verification.

Use `dpia.md`, `dpmp.md`, `privacy-notice.md`, `breach-runbook.md` and the verified
source mapping for counsel review. They are incomplete skeletons and leave the
DPIA/launch gate closed. Actual controller identity, bases, designation, notice,
legal/language/safeguarding approval, referral gaps and corpus/golden-set evidence
remain launch prerequisites; they do not block further private T8 engineering.
