.PHONY: lint
## Run linting
lint:
	pre-commit run --all-files

.PHONY: test
## Run tests
test:
	pytest tests