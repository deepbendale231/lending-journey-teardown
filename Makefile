PY ?= .venv/bin/python
VENV_BIN := $(dir $(PY))

.PHONY: help install rice sample-size metrics check final-check verify-rbi test cov lint format pdf all clean
help:          ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

install:       ## venv + test/lint dependencies (the tools themselves need only python3)
	python3 -m venv .venv && $(VENV_BIN)pip install -q -r requirements-dev.txt

rice:          ## score and rank 04_rice.csv, then show how robust the ranking is
	$(PY) -m tools.rice --write && $(PY) -m tools.rice

sample-size:   ## n per arm for the A/B test, with the arithmetic (edit the inputs in 07_ab_test_plan.md)
	$(PY) -m tools.sample_size $(ARGS)

metrics:       ## write reports/metrics.json, the README headline, the 07 sample-size block and the PRD evidence block
	$(PY) -m tools.metrics --write

check:         ## structure, evidence consistency, wording, numbers up to date
	$(PY) -m tools.rice --check && $(PY) -m tools.check

final-check:   ## everything in `check`, plus: no template markers, status complete, RBI rows verified by you, PDFs exported
	$(PY) -m tools.rice --check && $(PY) -m tools.check --final

verify-rbi:    ## sign off the RBI rows AFTER you have read the Directions: make verify-rbi INITIALS=DB
	$(PY) -m tools.verify_rbi --initials $(INITIALS) --i-have-read-the-directions

test:          ## unit tests for the tools
	$(PY) -m pytest -q

cov:           ## tests with the coverage gate used in CI
	$(PY) -m pytest -q --cov --cov-report=term-missing

lint:          ## ruff lint and format check
	$(VENV_BIN)ruff check . && $(VENV_BIN)ruff format --check .

format:
	$(VENV_BIN)ruff check --fix . && $(VENV_BIN)ruff format .

pdf:           ## export the PRD and the RICE table to exports/ (headless Chrome; see exports/README.md)
	$(PY) -m tools.export_pdf

all: rice metrics check cov lint   ## everything that does not need the evidence to be complete

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
