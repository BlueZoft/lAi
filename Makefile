.PHONY: setup lint typecheck schema hygiene test verify ingest serve eval

UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.local/uv-cache
RUN = $(UV) run --frozen --offline
HOST ?= 127.0.0.1
PORT ?= 8000
INGEST_ARGS ?= --manifest tests/fixtures/synthetic-act.manifest.json --raw tests/fixtures/synthetic-act.txt --text tests/fixtures/synthetic-act.txt

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

verify: lint typecheck schema hygiene test

ingest:
	$(RUN) python -m lai.corpus.cli ingest $(INGEST_ARGS)

serve:
	$(RUN) uvicorn lai.api:app --host $(HOST) --port $(PORT) --no-access-log

eval:
	@echo "UNAVAILABLE: evaluation is scheduled for T8. No metrics were produced." >&2
	@exit 2
