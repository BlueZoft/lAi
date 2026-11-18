# Private retrieval and measurement

T3 is an operator/research implementation. The HTTP API exposes health. Public
query routing must use T4 `SafetyNavigator`, followed by T5 answer assembly.
The full launch gate in README applies throughout.

## Run the deterministic workflow

```sh
make setup
make verify
make ingest
make eval
```

`make eval` reads five tiny invented queries and uses a deterministic feature-hash
embedding fake. It prints aggregate counts/metrics. All source text, queries and
vectors used by this workflow are synthetic. The result labels legal validation
UNVERIFIED.

For the optional database checks, use the dedicated development Compose stack.

```sh
docker compose up -d --wait db
make test-local
export UV_CACHE_DIR="$PWD/.local/uv-cache"
uv run --frozen --offline lai-retrieval --as-of 2026-11-18 demo --postgres
docker compose stop db
```

`test-local` creates and drops its own random synthetic test database. The demo
creates and deletes its own collection. Both use the generated local credential
and local socket/loopback route. The default verification suite excludes all
`local`, `gpu` and `network` tests and disables Internet sockets.

## Source and indexing contract

Use T2 `CorpusStore` acquisitions and a `VersionGraph`. `SourceCatalog` revalidates
source bytes and resolves exact section spans. A document's key combines its
instrument identity and language. Each chunk uses the stable T2 provision-version
node ID. The chunk text is the full verbatim section.

`index_document` prepares embeddings before replacing that document's index
entries. Quarantined or excluded versions publish no active sections. Acquisition
history remains available. `index_selected_records` first groups and validates
the complete requested active-source selection. Equivalent content uses canonical
provenance. Different unresolved versions for the same instrument/language cause
an error before updates. Choose the intended version explicitly with reviewed
graph/source evidence.

The PostgreSQL migration creates collection identities, acquisitions, active
document pointers and section vectors/weights. Migrations are transactionally
locked and checksummed. Changing an applied migration causes an error. Add a new
migration for future schema changes.

Each document replacement locks its collection, retains the acquisition,
deletes obsolete sections and publishes all new sections in one transaction.
A failed insertion rolls back the deletion. Repeated/concurrent updates retain
one active document version. Independent documents can be published incrementally.
Both search channels execute in one SQL statement and share its database snapshot.

Raw artefacts stay in ignored files and PostgreSQL is the query datastore.
The migration is included in the wheel. Model names, revisions and dimensions
bind each collection. Use a new collection for a different model configuration.

## Ranking and output checks

1. Validate bounded input, preserve Unicode NFC, and detect Latin/Sinhala/Tamil
   scripts. Mixed supported scripts retain a warning. Invalid control/private-use
   characters, unsupported scripts and mismatched language hints abstain.
2. Preserve the native query for direct cross-lingual embedding. Explicit
   `si-Latn` requires a supplied bounded transliterator. The default has none.
   The demonstration supplies one synthetic lookup. Unmapped inputs abstain.
3. Obtain dense and sparse vectors from the same backend identity. Dense vectors
   are finite, nonzero and normalised. Sparse weights are finite/nonnegative.
4. Rank by cosine similarity and sparse token-weight dot product independently.
   Fuse the two top-15 pools using reciprocal-rank constant 60. The PostgreSQL
   implementation uses exact cosine and a GIN sparse-key index.
5. Apply the configured dense floor and source scope. Revalidate each candidate
   against preserved source text and graph evidence. Check document-level and
   provision-level changes. Known amendment/repeal/supersession excludes affected
   text pending review.
6. Deduplicate logical instrument/section candidates across acquisitions and
   language versions. Return at least two candidates or an empty abstention.

Every candidate includes instrument type/number/year/section, language, actual
and canonical source URLs, source retrieval date/revision, acquisition ID, raw/
text/section hashes, original code-point span, amendment/commencement evidence
and staleness warnings. The acquisition date identifies source retrieval.
It never establishes current legal force. Age warnings use a provisional 90-day
acquisition interval. All results retain legal-currency/coverage uncertainty.

Default policy is disabled and synthetic-scoped. A private real-source research
instance must explicitly select `source_scope="real"` and enable its policy.
That scope excludes synthetic fixtures. The real model and real corpus still
need review and measurement before any public route is introduced.

The default dense floor is a provisional 0.5, with two minimum and five maximum
returned candidates. Evaluation can retain up to 15 validated candidates for
recall measurement. The internal ranking method serves aggregate evaluation,
while `retrieve` enforces the multi-candidate publication condition.

## Measured synthetic results

Memory and PostgreSQL runs on 18 November 2026 produced the following identical
results over five invented queries and three invented provisions.

| Metric | Observed value |
| --- | --- |
| Recall@1 | 0.9 |
| Recall@5 | 1.0 |
| Recall@15 | 1.0 |
| Mean reciprocal rank | 1.0 |
| Abstention rate | 0.8 |
| Dense floor for this fake | 0.05 |

Four single-match queries abstain under the two-candidate rule. One query has
two labelled relevant sections, so Recall@1 for that case is 0.5. The table
measures the deterministic fixture. Legal retrieval recall and calibration are
UNVERIFIED. The government-service benchmark in the original brief remains a
separate unverified research input.

## Local BGE-M3 profile on TARGET B

The optional `models` extra is frozen in `uv.lock`. It uses CPU PyTorch wheels
for Linux x86-64 and FlagEmbedding 1.4.2. Installation, weight acquisition,
real inference and capacity were not executed in this container. They remain
UNVERIFIED. The locked default setup installs only the lightweight app/test
dependencies.

Run the following online installation/acquisition phase on the laptop. The
acquisition helper takes a model revision and a destination, with no query
input. It resolves `main` to an immutable commit, preserves available notices,
checks supplied publisher LFS hashes and creates a checksum manifest.

```sh
export UV_CACHE_DIR="$PWD/.local/uv-cache"
uv sync --frozen --extra models
uv run --frozen --extra models python scripts/fetch_embedding_model.py --revision main
```

Record the printed revision and use its directory under `models/bge-m3/`.
Model files and manifests stay ignored. Runtime loading checks an acquisition
manifest when present, uses local paths, sets HuggingFace/Transformers offline
flags and disables remote model code. Existing externally verified model
directories can be supplied with their own fixed revision.

For actual evaluation, prepare a reviewed active-record selection, source graph
and a labelled dataset matching `schemas/evaluation-dataset.schema.json` under
ignored `data/`. Query scenarios must be invented or otherwise contain no real
personal data. Relevant IDs are the exact provision-version chunk IDs.
The following command shows the required operator-supplied values.

```text
uv run --frozen --offline --extra models lai-retrieval evaluate-local
  --store data/corpus --graph data/reviewed-graph.json --dataset data/legal-eval.json
  --record-id RECORD_ID --model-path models/bge-m3/REVISION --revision REVISION
```

Repeat `--record-id` for distinct selected instruments/languages. Evaluation
emits aggregate metrics and the provisional threshold, and retains legal
validation as UNVERIFIED. A reviewed Singlish adapter must be supplied through
the Python interface for real Singlish measurements. The default abstains.

The adapter checks the model's 8192-token context before encoding full sections.
Oversized sections fail before silent truncation. Use batch size one initially.
Measure CPU RAM, latency and quality on the 16 GB laptop. GPU, quantisation,
ONNX, subsection subdivision and reranking require separate measured choices.
The 4 GB GPU's capacity is UNVERIFIED.

The documented upstream interface provides 1024-dimensional dense vectors and
sparse token weights. The adapter contract is tested using stubs. Actual SDK/
weights integration remains a laptop check. [BGE-M3 documentation](https://github.com/FlagOpen/FlagEmbedding/tree/master/research/BGE_M3)

## Local connection privacy

The cloud daemon's internal Docker network exposed no TCP mapping despite its
configured port. A private Unix socket makes the real driver tests usable with
that network. `.local/` is owner-only, including when uv creates it before setup.
The libpq passfile is mode 0600, temporary and absent from driver arguments as a
raw password value. Connection failures expose a fixed code.

A development credential exposed by the initial failing test traceback was
rotated. The turn log records recovery with the value omitted. Full query-log,
retention and runtime-egress validation still belongs to T7.
