.PHONY: install format lint test run

install:
	python -m pip install -e ".[dev]"

format:
	ruff format .

lint:
	ruff check .

test:
	PYTHONPATH=src python -m unittest discover -s tests

run:
	PYTHONPATH=src python -m maie

