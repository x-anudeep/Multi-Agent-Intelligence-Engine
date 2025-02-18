.PHONY: install format lint test run api demo eval docker-build

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

api:
	PYTHONPATH=src python -m maie.api.cli

demo:
	PYTHONPATH=src python -m maie.demo.cli

eval:
	PYTHONPATH=src python -m maie.evaluation.cli examples/evals/workflow_eval_cases.json

docker-build:
	docker build -t maie:2.0.0 .
