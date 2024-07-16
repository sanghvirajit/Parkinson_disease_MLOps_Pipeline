from flask import Flask, request, jsonify
from pathlib import Path

from mlflow import MlflowClient
import mlflow

import pandas as pd
import os

MLFLOW_TRACKING_URI=os.getenv("MLFLOW_TRACKING_URI")
MODEL_NAME=os.getenv("MODEL_NAME")
EXPERIMENT_NAME=os.getenv("EXPERIMENT_NAME")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

client = MlflowClient()

# Get the latest versions of the registered model
latest_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])

# Print run_ids of all the latest versions
for version in latest_versions:
    RUN_ID = version.run_id

print(RUN_ID)

# logged_model = f'runs:/{RUN_ID}/model'
# # Load model as a PyFuncModel.
# loaded_model = mlflow.pyfunc.load_model(logged_model)

def load_model(run_id):
    logged_model = f'runs:/{run_id}/model'
    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    return loaded_model

print("Loading model from mlflow model registry...")
# Load model once in memory
loaded_model = load_model(RUN_ID)
print("Model loaded from mlflow model registry successfully!")

def prepare_features(data):
    processed_feature = pd.DataFrame(data, index=[0])
    return processed_feature

def predict(test_data):
    processed_data = prepare_features(test_data)
    preds = loaded_model.predict(processed_data)
    return float(preds[0])

app = Flask("parkinson-disease-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    
    test_data = request.get_json()
    pred = predict(test_data)

    if pred == 1:
        parkinson_diseases_prediction = "Yes"
    else:
        parkinson_diseases_prediction = "No"

    result = {"prediction": parkinson_diseases_prediction, "model_version": RUN_ID}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
