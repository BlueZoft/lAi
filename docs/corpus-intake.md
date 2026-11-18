# Corpus intake

T2 supplies an offline intake CLI and immutable staging artefacts. Source fetching
is an explicit operator action. The request-time application remains disabled.

## Run the synthetic path

From the existing checkout, run the following. It uses an invented instrument
whose number, publisher and domain are explicitly synthetic.

```sh
make setup
make ingest
make verify
```

`make ingest` stages three synthetic sections and prints a record hash, score,
section count and quarantine reasons. Repeating the same acquisition produces the
same record ID. Raw and extracted bytes are deduplicated independently by SHA-256.
All results stay under ignored `data/corpus/`.

For direct CLI use in this managed container, set the writable cache first.

```sh
export UV_CACHE_DIR="$PWD/.local/uv-cache"
uv run --frozen --offline lai-corpus --help
```

To check its generated graph, use the record ID printed by ingestion in the
`--graph` path. This command illustrates the path format.

```text
uv run --frozen --offline lai-corpus graph-check --graph data/corpus/graphs/RECORD_ID.json
```

## Prepare a source

1. Identify the original official document and its stable instrument/language
   identity. Record the actual acquisition URL, canonical publisher URL when
   known, publisher, timezone-aware acquisition time, source revision and licence
   evidence. Unknown source rights can be recorded as UNVERIFIED.
2. Keep original bytes and all extraction inputs under ignored `data/`. Obtain a
   trusted expected SHA-256 through the selected acquisition/source process.
   `scripts/fetch_source.py` accepts HTTPS, enforces checksums and a 32 MiB limit,
   preserves TLS verification and rejects a redirect to HTTP. Its output contains
   only a hash and byte count. Output paths must stay outside tracked content.
3. Run native extraction or the measured OCR/conversion tool on TARGET B. Keep
   its tool/version and extraction font metadata. Preserve the resulting UTF-8
   bytes exactly, including line endings. Record their SHA-256 separately.
4. Create a JSON manifest using `schemas/source-manifest.schema.json` and the
   synthetic fixture as a structural example. Replace every synthetic identity
   with verified metadata for a real source. Leave unknown number/year as null
   and `metadata_reviewed` false while review is pending.
5. Ingest explicitly. The following paths are examples for files prepared in
   the previous steps.

```sh
uv run --frozen --offline lai-corpus ingest \
  --manifest data/manifests/document.json \
  --raw data/raw/document.pdf \
  --text data/extracted/document.txt
```

The fetch command takes `--url`, `--sha256` and `--output`. Keep actual credentials
out of URLs, manifests and command arguments. The tool rejects user-info and
common credential-bearing URL parameters. No secret is required for the synthetic
workflow. Never copy real corpus text, metadata containing people, or PDFs into
tests, logs or Git.

## Upstream normalisation

The inspected government-documents pipeline has `doc.json`, `doc.pdf`, `doc.txt`
and `blocks.json` per language-version directory. Its metadata fields are
`doc_type`, `doc_id`, `num`, `date_str`, `description`, `url_metadata`, `lang`,
`url_pdf` and `doc_number`. The older Parliament pipeline instead has fields such
as `num`, `date`, `description`, `url_pdf_en`, `act_id` and `act_type`, and separate
native/OCR artefacts.

LAi's manifest adds acquisition provenance, expected raw/text hashes, instrument
identity, extraction details and review state. Build these fields from inspected
sources. An upstream publication date belongs in source research and must not be
substituted for the acquisition timestamp. Keep unknown extraction-tool versions
explicitly UNVERIFIED. Preserve upstream metadata outside Git for audit.

This release accepts normalised manifests. Full upstream batch adapters, bulk OCR
and extraction-tool reproducibility are pending TARGET B integration. The
inventory report distinguishes measured fields from summary counts.

## Eligibility and quarantine

`quality-v1` requires at least 80 visible characters, an alphabetic ratio of at
least 0.5, a declared-script ratio of at least 0.3, a score of at least 0.8 and no
quality issues. Combining marks are excluded from the alphabetic denominator.
The score starts with the alphabetic ratio divided by 0.7, capped at 1, with 0.25
subtracted per issue and a lower bound of zero. It is a provisional heuristic.

Replacement/control/private-use characters, common mojibake, repeated letters
and known FM Abhaya/DL-Manel-family fonts quarantine the document. Font metadata
may be incomplete. Some plausible-looking OCR or undeclared legacy text will
escape these heuristics. Human quality review and a labelled sample set remain
required before enabling a real corpus.

Parser issues, unreviewed source metadata, incomplete instrument identity or zero
parsed sections also block retrieval eligibility. English section spans index
Unicode code points into the original extraction. No whitespace normalisation
or arbitrary-window chunking changes the quoted text. Preambles and structural
headings remain in the preserved extraction. Schedules require review of the
whole document before retrieval eligibility. Sinhala/Tamil and non-Act parsers
currently return an unsupported reason.

A valid document can be staged successfully while `eligible_for_retrieval` is
false. Hash mismatches, invalid UTF-8, invalid manifests and oversized inputs
fail with exit 2. The CLI emits a generic error code, without the offending
payload. Model and schema validation add semantic checks beyond JSON structure.

## Manual foundational seeding

Use the stable gap IDs in `corpus-gaps.md`. Obtain the authoritative foundational
instrument, relevant amendments and commencement sources, retaining each as a
separate acquisition. Set `acquisition` to `manual_seed` and provide the relevant
`gap_ids`. A manual seed with no gap mapping is rejected. A synthetic pre-1981
example is covered by the tests.

Seeding alone leaves a gap OPEN. Closure requires a complete domain-specific
source inventory, readable source-anchored sections, language/version alignment,
evidenced amendment and commencement coverage, and recorded attorney review.
Unknown or unsupported material remains quarantined. No real gap closes in T2.

## Storage and recovery

| Path under the selected store | Contents |
| --- | --- |
| `raw/RAW_SHA256` | Original acquisition bytes |
| `text/TEXT_SHA256` | Exact UTF-8 extraction |
| `records/RECORD_ID.json` | Immutable provenance, quality and section record |
| `graphs/RECORD_ID.json` | Derived document/provision nodes |

The record is published after its required blobs. An interrupted attempt may
leave reusable orphan blobs. Retry the same acquisition to finish safely.
Existing artefacts with conflicting bytes cause an error. `CorpusStore.load`
checks record identity and recomputes intake against the stored raw/text blobs,
rejecting corruption or inconsistent derived fields. Graph files are derived
and can be recreated by repeating ingestion.

Each acquisition retains its source/revision/date observation. `select_canonical`
accepts equivalent content/identity candidates, prefers eligible reviewed
official sources, then ranks role, recency, URL and record ID deterministically.
Incompatible identities cause an error. Identical mirrored content keeps the
same version-node IDs. Choose a canonical observation before combining duplicate
version nodes in a graph.

## Version evidence

Use document/provision nodes and explicit amends, repeals, commences or supersedes
edges. Every edge has a source record, exact span/hash, review state and an
optional effective date. Structural validation rejects dangling endpoints,
self-links, mismatched evidence, cross-provision supersession and cycles.
`graph-check` revalidates source records and edge anchors against staged bytes.

The Python `VersionGraph.status` interface requires source records and extracted
texts and checks their evidence before returning recorded status. Undated,
unreviewed or future-effective edges retain explicit warnings. All results retain
`coverage_unverified`. No automatic amendment application or consolidation is
implemented. An effective date filters recorded instrument evidence and never
calculates a person's limitation deadline.

## Measure a local sample

This command reports scores, hashes, counts and fixed reason codes. It does not
emit document text, titles, parties or source metadata values.

```sh
uv run --frozen --offline python scripts/measure_corpus_sample.py \
  --text data/extracted/document.txt \
  --blocks data/extracted/blocks.json \
  --language en
```

`--blocks` is optional. Preserve extraction font metadata when available to
exercise legacy-font detection. Use `si` and `ta` for quality measurement while
their structural parsers remain pending. Record separate human-labelled OCR,
parsing and legal-coverage results on the laptop. Software tests use only tiny
invented fixtures.
