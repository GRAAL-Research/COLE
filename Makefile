.PHONY: lint format test build docker all

lint:
	pylint src/ tests/
	cd frontend && npm run lint

format:
	black --check .

test:
	pytest

build:
	cd frontend && npm ci && npm run build

docker:
	docker build -t cole .

all: format lint test build
