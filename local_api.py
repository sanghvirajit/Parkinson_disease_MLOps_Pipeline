from flask import Flask, request, jsonify

from mlflow import MlflowClient
import mlflow

import pandas as pd
import os
import time

from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MODEL_NAME = os.getenv("MODEL_NAME")
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

client = MlflowClient()

# Get the latest versions of the registered model
latest_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])

# Print run_ids of all the latest versions
for version in latest_versions:
    RUN_ID = version.run_id

print(RUN_ID)
def load_model(run_id):
    logged_model = f"runs:/{run_id}/model"
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


app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])
PREDICTION_COUNT_YES = Counter('parkinson_disease_predictions_yes', 'Yes Count', ['method', 'endpoint'])
PREDICTION_COUNT_NO = Counter('parkinson_disease_predictions_no', 'No Count', ['method', 'endpoint'])

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})


@app.route("/predict", methods=['POST'])
def predict_endpoint():
    
    start_time = time.time()
    REQUEST_COUNT.labels(method='POST', endpoint='/predict').inc()

    test_data = request.get_json()
    pred = predict(test_data)

    if pred == 1:
        parkinson_diseases_prediction = "Yes"
        PREDICTION_COUNT_YES.labels(method='POST', endpoint='/predict').inc()
    else:
        parkinson_diseases_prediction = "No"
        PREDICTION_COUNT_NO.labels(method='POST', endpoint='/predict').inc()

    result = {"prediction": parkinson_diseases_prediction, "model_version": RUN_ID}

    REQUEST_LATENCY.labels(endpoint='/predict').observe(time.time() - start_time)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
