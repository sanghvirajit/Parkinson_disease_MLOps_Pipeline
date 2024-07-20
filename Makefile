.PHONY: lint
## Run linting
lint:
	pre-commit run --all-files

.PHONY: test
## Run tests
test:
	pytest tests


.PHONY: test
## Run integration-tests
integration_test:
	LOCAL_IMAGE_NAME="parkinson-disease-prediction" bash integraton-test/run.sh
