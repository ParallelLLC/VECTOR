.PHONY: venv install run test api docker

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -e .

install:
	pip install -e .

run:
	python -m vector.cli run-pipeline --users examples/users.csv --edges examples/edges.csv --posts examples/posts.csv --taxonomy examples/taxonomy.yaml --out ./out

api:
	uvicorn vector.service:app --reload

test:
	pytest -q

docker:
	docker build -t vector:latest .
	docker run --rm -p 8000:8000 vector:latest
