.PHONY: lint test type

lint:
poetry run ruff src tests
poetry run black --check src tests

type:
poetry run mypy src

test:
poetry run pytest
