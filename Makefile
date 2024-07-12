.PHONY: lint
## Run linting
lint:
	pre-commit run --all-files
