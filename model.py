import json
import base64
import boto3

import pandas as pd
import mlflow

import os 

def load_model(run_id, model_bucket):

    # Load model from the S3 or from local location
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return mlflow.pyfunc.load_model(model_location)
     
    # Load model as a PyFuncModel using the RUN_ID
    model_location = f"s3://{model_bucket}/{run_id}/artifacts"

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

            kinesis_endpoint_url =  os.getenv('KINESIS_LOCALSTACK_URL')
            if kinesis_endpoint_url is None:
                kinesis_client = boto3.client("kinesis")
            else:
                kinesis_client = boto3.client("kinesis", 
                                              endpoint_url=kinesis_endpoint_url, 
                                              aws_access_key_id="fakeAccessKeyId",
                                              aws_secret_access_key="fakeSecretAccessKey"
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
