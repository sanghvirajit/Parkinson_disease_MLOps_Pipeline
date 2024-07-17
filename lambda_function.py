import os
import model

PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'parkinson-output-stream')
RUN_ID = os.getenv('RUN_ID')

model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME,
    run_id=RUN_ID
)

def lambda_handler(event, context):
    # pylint: disable=unused-argument
    return model_service.lambda_handler(event)