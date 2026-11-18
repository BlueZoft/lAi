.PHONY: setup lint typecheck schema hygiene test safety test-local verify ingest serve eval review-packet model-demo ops-build ops-check ops-prepare acceptance

UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.local/uv-cache
RUN = $(UV) run --frozen --offline
HOST ?= 127.0.0.1
PORT ?= 8000
INGEST_ARGS ?= --manifest tests/fixtures/synthetic-act.manifest.json --raw tests/fixtures/synthetic-act.txt --text tests/fixtures/synthetic-act.txt
MODEL_REPORT ?= .local/t6-model-replay.json

setup:
	$(UV) sync --frozen
	$(RUN) python scripts/prepare_local.py

lint:
	$(RUN) ruff check .
	$(RUN) ruff format --check .

typecheck:
	$(RUN) mypy src tests scripts

schema:
	$(RUN) python scripts/validate_schemas.py

hygiene:
	$(RUN) python scripts/check_repository.py

test:
	$(RUN) pytest

safety:
	$(RUN) pytest -m "safety and not local and not gpu and not network"

test-local:
	$(RUN) pytest -o addopts="-ra --strict-markers" -m local tests/test_postgres.py

verify: lint typecheck schema hygiene test

ingest:
	$(RUN) python -m lai.corpus.cli ingest $(INGEST_ARGS)

serve:
	$(RUN) python -m lai.operations.runtime --loopback --host $(HOST) --port $(PORT)

eval:
	$(RUN) python -m lai.retrieval.cli demo

acceptance:
	$(RUN) python -m lai.evaluation

review-packet:
	$(RUN) python -m lai.answers.review --repository . --output .local/t5-review.html

model-demo:
	$(RUN) python -m lai.model_tasks.measure --mode fake --dataset tests/fixtures/model-tasks.json --output $(MODEL_REPORT)

ops-prepare:
	$(RUN) python -m lai.operations.prepare

ops-build:
	$(RUN) python scripts/prepare_runtime_build.py
	docker --host=unix:///var/run/docker.sock build --network=none --pull=false -f operations/Dockerfile -t lai-runtime:t7 .local/operations-build

ops-check:
	$(RUN) python -m lai.operations.drill
