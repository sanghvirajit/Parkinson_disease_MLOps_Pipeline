from pathlib import Path

import pandas as pd
import json
import pickle
import os
from model import prepare_features, load_model

assets_path = Path(__file__).parent / "assets"
model_path = Path(__file__).parent / "models/model.pkl"

# with open(model_path, 'rb') as file:
#     local_loaded_model = pickle.load(file)

test_cases = assets_path.glob("*.txt")

RUN_ID = os.getenv("RUN_ID")

# Read text files
def read_txt(file_path):
    with open(file_path, 'r') as file:
        # Read the contents of the file
        content = file.read()
    return content

def test_prepare_feature():

    test_data = {
                'Age': 67,
                'Gender': '1',
                'Ethnicity': '2',
                'EducationLevel': '1',
                'BMI': 24.77259403457728,
                'Smoking': '0',
                'AlcoholConsumption': 13.941385740391004,
                'PhysicalActivity': 2.472534322357399,
                'DietQuality': 9.593309739128369,
                'SleepQuality': 6.060992120577725,
                'FamilyHistoryParkinsons': '0',
                'TraumaticBrainInjury': '0',
                'Hypertension': '1',
                'Diabetes': '0',
                'Depression': '0',
                'Stroke': '0',
                'SystolicBP': 92,
                'DiastolicBP': 60,
                'CholesterolTotal': 193.1381868106296,
                'CholesterolLDL': 137.5175503762128,
                'CholesterolHDL': 25.482467035806813,
                'CholesterolTriglycerides': 313.66674876926953,
                'UPDRS': 58.99092096333794,
                'MoCA': 19.902233615718146,
                'FunctionalAssessment': 5.104914484020905,
                'Tremor': '0',
                'Rigidity': '1',
                'Bradykinesia': '1',
                'PosturalInstability': '0',
                'SpeechProblems': '0',
                'SleepDisorders': '1',
                'Constipation': '0'
            }
    
    preocessed_data = prepare_features(test_data)
    expected_output = pd.DataFrame

    assert expected_output == type(preocessed_data), "Expected output should be pandas dataframe"

def test_jsonl_cases():

    # Loop over all test cases
    for test_case in test_cases:
        
        test_data = read_txt(test_case)
        test_case_name = test_case.stem.split("__")[0]
        ground_truth = test_case.stem.split("__")[1]
        test_data = test_data.replace("'", '"')

        # Convert to JSON object
        data_json = json.loads(test_data)

        # Predict
        processed_data = prepare_features(data_json)
        s3_loaded_model = load_model(RUN_ID)
        y_pred = s3_loaded_model.predict(processed_data)

        assert int(ground_truth) == y_pred[0], f"Expected ground_truth {int(ground_truth)} but got {y_pred[0]} for test case {test_case_name}"