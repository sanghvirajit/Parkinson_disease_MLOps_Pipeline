import json
import base64
import boto3
import os

import pandas as pd
import mlflow

# connect to kinesis client
kinesis_client = boto3.client('kinesis')

# Environmental variables
RUN_ID = os.getenv("RUN_ID")
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'parkinson-output-stream')

def load_model(run_id):
    # Load model as a PyFuncModel using the RUN_ID
    logged_model = f"s3://s3-parkinson-disease-prediction/{run_id}/artifacts"
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    return loaded_model

print("Loading model...")
# Load model once in memory
loaded_model = load_model(RUN_ID)
print("Model loaded succeefully from S3!")

def prepare_features(data):
    processed_feature = pd.DataFrame(data, index=[0])
    return processed_feature

def predict(test_data):
    processed_data = prepare_features(test_data)
    preds = loaded_model.predict(processed_data)
    return float(preds[0]), RUN_ID

def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    parkinson_event = json.loads(decoded_data)
    return parkinson_event
        
def lambda_handler(event, context):
    
    predictions_events = []
    
    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        
        parkinson_event = base64_decode(encoded_data)
        
        data = parkinson_event['data']
        patient_id = parkinson_event['patient_id']
        
        processed_data = prepare_features(data)
        prediction, model_version = predict(processed_data)    
    
        if prediction == 1:
            parkinson_diseases_prediction = "Yes"
        else:
            parkinson_diseases_prediction = "No"
        
        prediction_event = {
                            "model": "parkinson_disease_prediction_model",
                            "version": model_version,
                            "prediction": {
                                        "parkinson_diseases_prediction": parkinson_diseases_prediction, 
                                        "patient_id": patient_id
                                        }
                            }
        
        kinesis_client.put_record(
                            StreamName=PREDICTIONS_STREAM_NAME,
                            Data=json.dumps(prediction_event),
                            PartitionKey=str(patient_id)
                        )
                        
        predictions_events.append(prediction_event)
    
    return {"predictions": predictions_events}
