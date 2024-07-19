#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

export LOCAL_IMAGE_NAME="parkinson-disease-prediction"
LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
export LOCAL_IMAGE_NAME="parkinson-disease-prediction:${LOCAL_TAG}"

docker build -t ${LOCAL_IMAGE_NAME} ..

sleep 5

docker-compose up -d

sleep 5

python test_docker.py
