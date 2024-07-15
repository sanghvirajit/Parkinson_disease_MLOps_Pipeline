from flask import Flask, request, jsonify

import mlflow

import pandas as pd
import os

RUN_ID = os.getenv("RUN_ID")

def load_model(run_id):
    # Load model as a PyFuncModel using the RUN_ID
    logged_model = f"s3://s3-parkinson-disease-prediction/{run_id}/artifacts"
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    return loaded_model

# Load model once in memory
loaded_model = load_model(RUN_ID)

def prepare_features(data):
    processed_feature = pd.DataFrame(data, index=[0])
    return processed_feature

def predict(test_data):
    processed_data = prepare_features(test_data)
    preds = loaded_model.predict(processed_data)
    return float(preds[0]), RUN_ID

app = Flask("parkinson-disease-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    test_data = request.get_json()
    pred, model_version = predict(test_data)

    if pred == 1:
        parkinson_diseases_prediction = "Yes"
    else:
        parkinson_diseases_prediction = "Yes"

    result = {"prediction": parkinson_diseases_prediction, "model_version": model_version}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
