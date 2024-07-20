#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

export LOCAL_IMAGE_NAME="parkinson-disease-prediction"
LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`

export LOCAL_IMAGE_NAME="parkinson-disease-prediction:${LOCAL_TAG}"

export AWS_ACCESS_KEY_ID="fakeAccessKeyId"
export AWS_SECRET_ACCESS_KEY="fakeSecretAccessKey"
export MODEL_BUCKET="s3-parkinson-disease-prediction"
export RUN_ID="477e0bfee6964438991021bfa605a2ed"
export PREDICTIONS_STREAM_NAME="kinesis-output-stream"
export LOCALSTACK_URL="http://localslack:4566/"

docker build -t ${LOCAL_IMAGE_NAME} ..

sleep 5

docker-compose up -d

sleep 5

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1

sleep 5

aws --endpoint-url=http://localhost:4566 s3 mb s3://${MODEL_BUCKET}
aws --endpoint-url=http://localhost:4566 s3 sync ../model s3://${MODEL_BUCKET}/${RUN_ID}/artifacts/

sleep 5

python test_docker.py
