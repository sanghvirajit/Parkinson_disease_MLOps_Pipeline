LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=parkinson-disease-prediction:${LOCAL_TAG}

.PHONY: lint
## Run linting
lint:
	pre-commit run --all-files

.PHONY: test
## Run tests
test:
	pytest unit_test


.PHONY: integration_test
## Run integration-tests
integration_test:
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} cd integration_test && ./run.sh
