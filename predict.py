from flask import Flask, request, jsonify

import mlflow

import pandas as pd
import os

RUN_ID = os.getenv("RUN_ID")

# Load model as a PyFuncModel using the RUN_ID
logged_model = f"s3://s3-parkinson-disease-prediction/{RUN_ID}/artifacts"
loaded_model = mlflow.pyfunc.load_model(logged_model)


def predict(test_data):
    preds = loaded_model.predict(pd.DataFrame(test_data, index=[0]))
    return float(preds[0])


app = Flask("parkinson-disease-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    test_data = request.get_json()
    pred = predict(test_data)

    if pred == 1:
        parkinson_diseases_prediction = "Yes"
    else:
        parkinson_diseases_prediction = "Yes"

    result = {"prediction": parkinson_diseases_prediction, "model_version": RUN_ID}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
