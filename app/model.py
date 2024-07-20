import json
import base64
import boto3

import pandas as pd
import mlflow

import os


def load_model(run_id, model_bucket):
    # # Option:1 load model from the local dir by specifiying the path to env var
    # # Load model from the S3 or from local location
    # model_location = os.getenv('MODEL_LOCATION')

    # if model_location is not None:
    #     return mlflow.pyfunc.load_model(model_location)

    # Load model as a PyFuncModel using the RUN_ID
    model_location = f"s3://{model_bucket}/{run_id}/artifacts"

    # Option:2 Load model from the s3 localstack by setting localstack endpoint in env var
    localstack_endpoint_url = os.getenv("LOCALSTACK_URL")
    if localstack_endpoint_url is not None:
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("LOCALSTACK_URL")
        # Else from the main aws account

    # Option3: Load model from aws s3
    return mlflow.pyfunc.load_model(model_location)


def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode("utf-8")
    parkinson_event = json.loads(decoded_data)
    return parkinson_event


class ModelService:
    def __init__(self, model, model_version=None, prediction_stream_name=None):
        self.model = model
        self.model_version = model_version
        self.prediction_stream_name = prediction_stream_name

    def prepare_features(self, data):
        processed_feature = pd.DataFrame(data, index=[0])
        return processed_feature

    def predict(self, features):
        preds = self.model.predict(features)
        return float(preds[0])

    def lambda_handler(self, event):
        predictions_events = []
        for record in event["Records"]:
            encoded_data = record["kinesis"]["data"]
            parkinson_event = base64_decode(encoded_data)

            data = parkinson_event["data"]
            patient_id = parkinson_event["patient_id"]

            features = self.prepare_features(data)
            prediction = self.predict(features)

            if prediction == 1:
                parkinson_diseases_prediction = "Yes"
            else:
                parkinson_diseases_prediction = "No"

            prediction_event = {
                "model": "parkinson_disease_prediction_model",
                "version": self.model_version,
                "prediction": {
                    "parkinson_diseases_prediction": parkinson_diseases_prediction,
                    "patient_id": patient_id,
                },
            }

            localstack_endpoint_url = os.getenv("LOCALSTACK_URL")
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            if localstack_endpoint_url is None:
                # read from the aws kinesis
                kinesis_client = boto3.client("kinesis")
            else:
                kinesis_client = boto3.client(
                    "kinesis",
                    endpoint_url=localstack_endpoint_url,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                )

            kinesis_client.put_record(
                StreamName=self.prediction_stream_name,
                Data=json.dumps(prediction_event),
                PartitionKey=str(patient_id),
            )

            predictions_events.append(prediction_event)

        return {"predictions": predictions_events}


def init(prediction_stream_name: str, run_id: str, model_bucket: str):
    model = load_model(run_id, model_bucket)
    model_service = ModelService(
        model=model, model_version=run_id, prediction_stream_name=prediction_stream_name
    )
    return model_service
