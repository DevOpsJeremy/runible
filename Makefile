.PHONY: pre-build build install pre-test test pre-lint lint pre-format format clean all
define HEADER
	@printf "\n-----\n%s\n-----\n\n" "$@"
endef

pre-build:
	$(HEADER)
	pip install build

build: pre-build
	$(HEADER)
	python -m build

install:
	$(HEADER)
	pip install .

pre-test:
	$(HEADER)
	pip install pytest .

test: pre-test
	$(HEADER)
	pytest

pre-lint:
	$(HEADER)
	pip install ruff

lint: pre-lint
	$(HEADER)
	ruff check
	ruff format --check

pre-format:
	$(HEADER)
	pip install ruff

format: pre-format
	$(HEADER)
	ruff format

clean:
	$(HEADER)
	rm -rf dist
	rm -f *junit.xml

all: clean install test lint
