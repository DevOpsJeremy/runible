.PHONY: pre-build build install pre-test test pre-lint lint pre-format format clean all run
define HEADER
	@printf "\n-----\n%s\n-----\n\n" "$@"
endef

define CLEAN
	@$(foreach f,$(1),find . -name '$(f)' -exec rm -vrf {} +;)
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

all: clean install test lint

run: install
	$(CMD) run $(RUNIBLE_RUN_FILE)

pre-docs:
	pip install zensical mkdocstrings-python

docs: pre-docs
	zensical build

LINT_TRASH_FILES := .ruff_cache
clean-lint:
	$(call CLEAN,$(LINT_TRASH_FILES))

TEST_TRASH_FILES := .pytest_cache pytest.junit.xml __pycache__
clean-test:
	$(call CLEAN,$(TEST_TRASH_FILES))

DOCS_TRASH_FILES := .cache site
clean-docs:
	$(call CLEAN,$(DOCS_TRASH_FILES))

BUILD_TRASH_FILES := dist
clean-build:
	$(call CLEAN,$(BUILD_TRASH_FILES))

TRASH_FILES := 
clean:
	$(HEADER)
	$(call CLEAN,$(TRASH_FILES))


