import os
from app import model

PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME")
RUN_ID = os.getenv("RUN_ID")
MODEL_BUCKET = os.getenv("MODEL_BUCKET")

model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME,
    run_id=RUN_ID,
    model_bucket=MODEL_BUCKET,
)


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    return model_service.lambda_handler(event)
