.PHONY: pre-build build install pre-test test pre-lint lint pre-format format clean all run
define HEADER
	@printf "\n-----\n\x1b[$(COLOR_CODE)m%s\x1b[0m\n-----\n\n" "$@"
endef

define CLEAN
	@$(foreach f,$(1),find . -name '$(f)' -exec rm -vrf {} +;)
endef

CMD ?= runible
RUNIBLE_RUN_FILE ?= examples/runible.yml
COLOR_CODE ?= 34

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

all: clean install test lint

run: install
	$(CMD) run $(RUNIBLE_RUN_FILE)

pre-docs: install
	pip install zensical mkdocstrings-python

DOCS_ARGS ?= --clean
docs: pre-docs
	zensical build $(DOCS_ARGS)

LINT_TRASH_FILES ?= .ruff_cache
clean-lint:
	$(HEADER)
	$(call CLEAN,$(LINT_TRASH_FILES))

TEST_TRASH_FILES ?= .pytest_cache pytest.junit.xml __pycache__
clean-test:
	$(HEADER)
	$(call CLEAN,$(TEST_TRASH_FILES))

DOCS_TRASH_FILES ?= .cache site
clean-docs:
	$(HEADER)
	$(call CLEAN,$(DOCS_TRASH_FILES))

BUILD_TRASH_FILES ?= dist
clean-build:
	$(HEADER)
	$(call CLEAN,$(BUILD_TRASH_FILES))

TRASH_FILES ?= 
clean: clean-lint clean-test clean-docs clean-build
	$(HEADER)
	$(call CLEAN,$(TRASH_FILES))

