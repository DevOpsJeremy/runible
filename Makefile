.PHONY: pre-build build install pre-test test pre-lint lint pre-format format clean all run
define HEADER
	@printf "\n-----\n%s\n-----\n\n" "$@"
endef

define CLEAN
	@$(foreach f,$(1),find . -name '$(f)' -exec rm -vrf {} +;)
endef

CMD ?= runible
RUNIBLE_RUN_FILE ?= examples/runible.yml

PYTHON_BUILD_VERSION ?= 1.5.0
install-build:
	$(HEADER)
	pip install build==$(PYTHON_BUILD_VERSION)

pre-build: install-build

build: pre-build
	$(HEADER)
	python -m build

install:
	$(HEADER)
	pip install .

PYTHON_PYTEST_VERSION ?= 9.1.1
install-pytest:
	$(HEADER)
	pip install pytest==$(PYTHON_PYTEST_VERSION)

pre-test: install install-pytest

test: pre-test
	$(HEADER)
	pytest

PYTHON_RUFF_VERSION ?= 0.16.4
install-ruff:
	$(HEADER)
	pip install ruff==$(PYTHON_RUFF_VERSION)

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

PYTHON_ZENSICAL_VERSION ?= 0.0.57
PYTHON_MKDOCSTRINGS_VERSION ?= 2.0.7
DOCS_PACKAGES ?= zensical==$(PYTHON_ZENSICAL_VERSION) mkdocstrings-python==$(PYTHON_MKDOCSTRINGS_VERSION)
docs-install: install
	pip install $(DOCS_PACKAGES)

docs-generate:
	python docs/scripts/gen_ref_pages.py

pre-docs: docs-install docs-generate

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

NPM_CSPELL_VERSION ?= 10.1.0
install-cspell:
	$(HEADER)
	npm install -g cspell@$(NPM_CSPELL_VERSION)

pre-spell-check: install-cspell

spell-check: pre-spell-check
	$(HEADER)
	# Run the cspell CLI. Ensure cspell is installed (see `make spell-check-install`).
	cspell

TRASH_FILES ?= 
clean: clean-lint clean-test clean-docs clean-build
	$(HEADER)
	$(call CLEAN,$(TRASH_FILES))

