from flask import Flask, request, jsonify
from pathlib import Path
import pickle

import mlflow

import pandas as pd
import os

# # Load model from S3
# RUN_ID = os.getenv("RUN_ID")

# def load_model(run_id):
#     # Load model as a PyFuncModel using the RUN_ID
#     logged_model = f"s3://s3-parkinson-disease-prediction/{run_id}/artifacts"
#     loaded_model = mlflow.pyfunc.load_model(logged_model)
#     return loaded_model

# # Load model once in memory
# loaded_model = load_model(RUN_ID)

# Load local model
model_path = Path(__file__).parent / "models/model.pkl"

with open(model_path, 'rb') as file:
    loaded_model = pickle.load(file)

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

    result = {"prediction": parkinson_diseases_prediction, "model_version": "6f4c13e86ae94d7a958349c35af3fbb1"}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
