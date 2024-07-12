import requests

test_data = {
            'Age': 67,
            'BMI': 24.77259403457728,
            'AlcoholConsumption': 13.941385740391004,
            'PhysicalActivity': 2.472534322357399,
            'DietQuality': 9.593309739128369,
            'SleepQuality': 6.060992120577725,
            'SystolicBP': 92,
            'DiastolicBP': 60,
            'CholesterolTotal': 193.1381868106296,
            'CholesterolLDL': 137.5175503762128,
            'CholesterolHDL': 25.482467035806813,
            'CholesterolTriglycerides': 313.66674876926953,
            'UPDRS': 58.99092096333794,
            'MoCA': 19.902233615718146,
            'FunctionalAssessment': 5.104914484020905,
            'Gender': '1',
            'Ethnicity': '2',
            'EducationLevel': '1',
            'Smoking': '0',
            'FamilyHistoryParkinsons': '0',
            'TraumaticBrainInjury': '0',
            'Hypertension': '1',
            'Diabetes': '0',
            'Depression': '0',
            'Stroke': '0',
            'Tremor': '0',
            'Rigidity': '1',
            'Bradykinesia': '1',
            'PosturalInstability': '0',
            'SpeechProblems': '0',
            'SleepDisorders': '1',
            'Constipation': '0'
        }

url = 'http://localhost:9696/predict'
response = requests.post(url, json=test_data)
print(response.json())