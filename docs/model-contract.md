# T6 bounded local model contract

19 November 2026. This is a private research interface, separate from the answer
API. `BoundedModel` cannot enable navigation, approve a gloss, choose a referral
or change a safety decision. T5 still displays full original provisions with
reviewed glosses. No model-generated Sinhala explanation is displayed.

The existing reviewer/source prerequisites do not block this engineering work.
Actual language quality, legal recall, runtime isolation and laptop capacity are
UNVERIFIED. No model has been downloaded or run in the cloud for T6.

## Executable contracts and fallbacks

`src/lai/model_tasks/contracts.py` and five committed `model-*` /
`local-model-manifest` schemas define the boundary. The per-task prompt schemas
come from the same strict output types. All fields reject extras and coercion.
`prompts.py` records `bounded-v1`, frames the input as JSON data and forbids legal
conclusions, recommendations, deadlines, citations and tool/network actions.
Prompt instructions alone are insufficient; validators are mandatory.

| Task | Accepted proposal | Deterministic failure behaviour |
| --- | --- | --- |
| `language` | Sorted Unicode scripts; language consistent with scripts and explicit hint | Return deterministic scripts/hint only. Latin script does not distinguish English from Singlish. |
| `transliterate` | Explicit `si-Latn` input; bounded Sinhala-script output | Return no transliteration. Script validity establishes no semantic accuracy. |
| `intent` | One fixed T4 domain or `unknown`, consistent with deterministic domains | Return `unknown`; preserve the original safety decision. |
| `entities` | At most eight ordered exact spans: ISO dates, explicitly marked amounts, known English district names, literal employment status | Return no entities. No inferred facts, ambiguous date conversion or arithmetic. |
| `rewrite` | At most eight ordered original-input spans, total 256 characters | Retain the complete original query. No generated synonyms, translation or added facts. |
| `extractive_summary` | At most three exact source spans, total 768 characters, tied to the supplied text SHA-256 | Return no summary. This research selection never replaces T5's full provision. |

Dates are calendar-validated only. Amounts require `LKR 100.00` / `Rs. 100.00`
style markers, with no grouping separators; their lexical value is preserved.
District/status aliases in Sinhala and Tamil are intentionally unsupported until
reviewed. Exact-span checks prove copying, not factual truth, legal relevance,
completeness or correct interpretation. Tamil contract coverage is not Tamil
product delivery. The tiny Singlish/Sinhala seeds are UNREVIEWED measurement data.

Every request scans the raw bounded scenario through T4 **before** validating
the model envelope or acquiring a model slot. Urgent signals, forbidden advice,
limitation and wider-risk domains return the unchanged safety route with no
model call. Invalid input also stops. The private research harness may measure
otherwise unsupported Tamil/Singlish or unknown low-risk text; its outcome
always has `product_enabled: false`. It has no retrieval/assembly integration.
Do not put this facade in front of product triage or use it to override that
triage's language abstention.

Replies must be one JSON object, at most 8 KiB. Duplicate keys, non-JSON wrappers,
wrong tasks/types, extra fields, invented/overlapping/unordered/out-of-range spans,
changed source hashes and script/intent disagreements are discarded. Offsets
refer to Python Unicode code points in the unmodified input, end exclusive.
Source excerpts are capped at 4,096 characters; scenarios retain T4's 1,024 limit.

`TaskOutcome.output` contains only a validated research proposal. Failures have
no model output; `deterministic_output` contains the scripts, unknown intent,
empty entities or whole original query where appropriate. Transliteration and
summary failure return neither. Busy, unavailable, timed-out or malformed
backends use the same fixed per-task fallback and fixed reason codes. Never log
the outcome: its original-query fallback can contain private input.

## Local runner and budget

`LlamaCppBackend` launches a pinned **llama-completion** executable for each
call. It sends the prompt on stdin, uses a per-task JSON grammar and has no
server endpoint. The clean child environment omits application credentials and
proxies. Stderr is discarded; stdout is bounded and validated. A single slot
shared by model facades in one Python process rejects concurrent work rather
than queueing it. It cannot coordinate unrelated processes or embedding jobs.

The deadline covers pipe writes, reads and process wait. Each owned process
group is killed and the direct child reaped on success/failure, releasing its
model residency. Changed executable/GGUF hashes fail before inference. The model
and executable must remain immutable during a run; shared-library provenance
and operating-system resource/network enforcement remain operator/T7 concerns.

`config/model-budget.json` records CPU defaults:

| Resource | Provisional admission/limit; not a fit measurement |
| --- | --- |
| Model | 3–4.5B declared parameters, Q4_K_M, GGUF at most 3,072 MiB |
| Context/output | 2,048 context tokens; 256 generated tokens; no context shifting |
| CPU | Two threads; at least 6,144 MiB currently available RAM before launch |
| Process RAM | Sampled RSS/high-water target 8,192 MiB; stop on an observed breach |
| GPU | Default zero layers; optional eight-layer probe on NVIDIA device 0 |
| VRAM | At most 3,072 MiB sampled total device use, including the desktop; reserve the remaining 1 GiB on the 4 GiB laptop |
| Time | 120 seconds per child invocation; 16 KiB prompt byte cap |

Budget available laptop RAM for OS/desktop, application/database and exactly one
heavy model stage. Start with embeddings on CPU, then terminate that process
before loading the instruct model. Do not co-reside BGE-M3, reranker, OCR and the
instruct model on the 4 GiB GPU. Eight offloaded layers are an experiment, not a
claim that a particular architecture fits. Reranking remains deferred.

RAM is sampled every selector cycle (roughly 50 ms); GPU is sampled roughly every
500 ms through `nvidia-smi`, which itself has a two-second timeout. These are
sampled observations and stop conditions, not hard memory isolation or guaranteed
peaks. Missing/over-budget GPU telemetry rejects GPU execution. Use a fresh CPU
run after GPU failure. CPU mode hides CUDA and passes zero GPU layers; CPU
llama.cpp builds avoid other accelerator backends. T7 must add OS-level no-egress
and resource controls. Offline flags do not establish network isolation.

## Cloud demonstration, without a model

From the repository root with Python 3.12 and uv:

```sh
make setup
make verify
make model-demo
```

The report is `.local/t6-model-replay.json`, mode 0600. The fake copies the
dataset's expected labels and is explicitly marked `backend_kind: fake`.
Perfect matching is a plumbing check, never measured Sinhala capability.
Reports refuse to overwrite existing files. For another run:

```sh
make model-demo MODEL_REPORT=.local/t6-model-replay-second.json
```

## TARGET B: prepare independently, outside runtime

Use the laptop only. No home-lab connection, paid service or real personal
situations are needed. Install Python 3.12/uv and a native compiler/CMake through
the laptop's normal package manager. Obtain a licensed 4B-class Q4_K_M GGUF from
its publisher at an immutable revision; preserve its licence/model card and
trusted SHA-256 outside Git. No checkpoint is pre-approved for Sinhala. Model
selection, licence checks, acquisition and actual inference remain UNVERIFIED.

Build the inspected llama.cpp revision (download/build commands are installation,
not request-time actions):

```sh
git clone https://github.com/ggml-org/llama.cpp .local/llama.cpp
git -C .local/llama.cpp checkout --detach edec462cc00abebc50610b82ac06c6cde266e5d0
cmake -S .local/llama.cpp -B .local/llama.cpp/build-cpu \
  -DGGML_CUDA=OFF -DLLAMA_BUILD_SERVER=OFF -DLLAMA_BUILD_APP=OFF \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_OPENSSL=OFF
cmake --build .local/llama.cpp/build-cpu --target llama-completion -j 2
```

The above native build was **not executed here**. Inspect its build provenance,
licence and `--help`; retain the executable checksum from your own build. Use
`llama-completion`, because the inspected parser restricts `--no-conversation` to
that executable; newer `llama-cli` is a different interface. This adapter sends
a plain bounded-task prompt, with no model-specific chat template. Quality or
template changes require a new prompt version and repeated measurement.

Replace the checksum/revision/evidence placeholders below with your actual
values. The model file is an example local name, not a supplied download. The
pinning command compares both trusted expected hashes with local files and
refuses existing output. It does not authenticate the publisher or verify the
operator's parameter/quantisation/licence assertions.

```sh
uv --cache-dir .local/uv-cache run --frozen --offline python -m lai.model_tasks.pin \
  --model models/instruct-4b-q4.gguf \
  --executable .local/llama.cpp/build-cpu/bin/llama-completion \
  --model-id '<publisher/model-id>' --revision '<immutable-model-revision>' \
  --runner-revision edec462cc00abebc50610b82ac06c6cde266e5d0 \
  --parameters-billions 4.0 --licence-evidence-ref '<retained-model-card-and-licence-reference>' \
  --expected-model-sha256 '<trusted-64-hex-model-sha256>' \
  --expected-executable-sha256 '<own-build-64-hex-executable-sha256>' \
  --output .local/instruct-cpu-manifest.json
```

Do not use the placeholder parameter count for a different-sized model. A
licence reference is an evidence pointer, not legal approval. Keep artefacts,
manifests and reports ignored; do not add weights or real query samples to Git.

## TARGET B: sequential CPU and optional GPU measurements

First install the optional frozen embedding profile and acquire BGE-M3 with the
existing `scripts/fetch_embedding_model.py --revision <immutable-ref>` helper;
see `retrieval.md` for notices/checksums. This installation needs network; the
probe does not. Replace `<bge-commit>` below with its resolved snapshot commit.

```sh
uv --cache-dir .local/uv-cache sync --frozen --extra models
uv --cache-dir .local/uv-cache run --frozen --offline --extra models \
  python scripts/measure_embedding_capacity.py \
  --model-path models/bge-m3/<bge-commit> --revision '<bge-commit>' \
  --output .local/t6-bge-cpu.json
```

Wait for this process to exit. It encodes three fixed invented multilingual
strings on CPU and records process high-water RAM and cold load/encode latency;
it records neither vectors nor texts and establishes no legal recall. A missing
snapshot integrity manifest fails. Then run the independent instruct stage:

```sh
uv --cache-dir .local/uv-cache run --frozen --offline python -m lai.model_tasks.measure \
  --mode cpu --dataset tests/fixtures/model-tasks.json \
  --manifest .local/instruct-cpu-manifest.json --model models/instruct-4b-q4.gguf \
  --executable .local/llama.cpp/build-cpu/bin/llama-completion \
  --repetitions 3 --output .local/t6-instruct-cpu.json
```

Each call loads/exits independently; latency includes cold start and repeated
integrity hashing, not warm-service latency. A 256-token or 2,048-context cap can
produce fallback on long Sinhala/JSON; count these failures rather than raising
limits without remeasurement. No inference tool is installed by this command.

Only after CPU execution works, optionally build a separate CUDA version with
`-DGGML_CUDA=ON` (and a working laptop CUDA toolchain), pin that binary in a new
manifest and repeat with `--mode gpu`, its matching manifest/executable and a
fresh report path. The GPU mode offloads eight layers. No driver/toolchain was
installed here. Missing NVIDIA telemetry means CPU fallback; AMD/other GPU
backends are not measured by this probe. Keep other GPU workloads stopped and
compare total VRAM baseline before/after using `nvidia-smi`. Process exit, not a
cache-clearing assertion, separates residency stages. Do not run stages in parallel.

Reports contain counts by task/language, validated/fallback/blocked counts,
exact matches, p50/p95/max latency, dataset/prompt/model/binary identities and
sampled RAM/VRAM. They exclude input/reply text, case identifiers and host paths.
All `resource_fit`, `sinhala_capability` and `legal_validation` labels stay
UNVERIFIED; numeric samples alone do not set a release flag. A report may be
successfully written even if every local call fell back: inspect the counts.

Have the language reviewer correct/expand an ignored synthetic dataset for
Sinhala, mixed script, dialects and Singlish. Retain its exact revision/hash and
review evidence, include negative/ambiguous cases, and compare accepted text
manually. Exact match undercounts valid alternative transliterations and does
not measure semantic accuracy. Record task quality and fallback rates separately
from urgent-route tests and legal retrieval evaluation. No numeric production
threshold is selected from these seeds. T8 needs the independent reviewed golden
set. Your pending safety/UI/gloss/referral review remains in `reviewer-handoff.md`.

## Inspected upstream evidence

On 19 November 2026, inspected llama.cpp at commit
`edec462cc00abebc50610b82ac06c6cde266e5d0` through GitHub/raw GETs:

| File | SHA-256 | Observation |
| --- | --- | --- |
| [common/arg.cpp](https://github.com/ggml-org/llama.cpp/blob/edec462cc00abebc50610b82ac06c6cde266e5d0/common/arg.cpp) | `62fc49bc26066aa2459a99e2290beb136ced4f0bef15c6ce516dad568883e8c2` | JSON schema, stdin-file, context/GPU/IO/log flags; no-conversation is completion-only. |
| [tools/completion/completion.cpp](https://github.com/ggml-org/llama.cpp/blob/edec462cc00abebc50610b82ac06c6cde266e5d0/tools/completion/completion.cpp) | `0dde1fed7b17e9b37ad0cf3e125210dd1c316364cf2924f24d0f41c38538677b` | Oversized initial prompts fail; context shifting can be disabled. |
| [CMakeLists.txt](https://github.com/ggml-org/llama.cpp/blob/edec462cc00abebc50610b82ac06c6cde266e5d0/CMakeLists.txt) | `6727a1188ab844d2eb5af5aa6ee07c50b80a5bb8711b9cad0784db1939587d1b` | Tools/server/app/OpenSSL build options; old CURL option is deprecated. |

This establishes source-interface observations, not an executed native build,
model licence, backend compatibility, Sinhala competence or network isolation.
