.PHONY: pre-build build install pre-test test pre-lint lint pre-format format clean all run
define HEADER
	@printf "\n-----\n%s\n-----\n\n" "$@"
endef

CMD?=runible
RUNIBLE_RUN_FILE?=examples/runible.yml

pre-build:
	$(HEADER)
	pip install build

build: pre-build
	$(HEADER)
	python -m build

install:
	$(HEADER)
	pip install .

install-ruff:
	$(HEADER)
	pip install ruff

pre-test:
	$(HEADER)
	pip install pytest .

test: pre-test
	$(HEADER)
	pytest

pre-lint: install-ruff

lint: pre-lint
	$(HEADER)
	ruff check
	ruff format --check

pre-format: install-ruff

format: pre-format
	$(HEADER)
	ruff format

lint-fix: pre-lint
	$(HEADER)
	ruff check --fix

fix: format lint-fix

TRASH_FILES := dist *junit.xml .*_cache *.cache __pycache__ site
clean:
	$(HEADER)
	@$(foreach f,$(TRASH_FILES),find . -name '$(f)' -exec rm -vrf {} +;)

all: clean install test lint

run: install
	$(CMD) run $(RUNIBLE_RUN_FILE)
