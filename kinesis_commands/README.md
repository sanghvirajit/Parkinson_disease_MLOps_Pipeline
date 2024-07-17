### Build and Run Docker with all enviromental variables

```bash
docker build -t parkinson-disease-prediction:latest .

docker run -it --rm \
    -p 9696:9696 \
    -e RUN_ID="${RUN_ID}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    parkinson-disease-prediction:latest
```

test the docker using following command:

```bash
python test.py
```

it should give following results:

![Example Image](assets/348293521-8733603d-2c78-4b20-90e1-c383665c573c.png)

### Record Example

```bash
{
   "data": {
         "Age": 67,
         "Gender": "1",
         "Ethnicity": "2",
         "EducationLevel": "1",
         "BMI": 24.77259403457728,
         "Smoking": "0",
         "AlcoholConsumption": 13.941385740391004,
         "PhysicalActivity": 2.472534322357399,
         "DietQuality": 9.593309739128369,
         "SleepQuality": 6.060992120577725,
         "FamilyHistoryParkinsons": "0",
         "TraumaticBrainInjury": "0",
         "Hypertension": "1",
         "Diabetes": "0",
         "Depression": "0",
         "Stroke": "0",
         "SystolicBP": 92,
         "DiastolicBP": 60,
         "CholesterolTotal": 193.1381868106296,
         "CholesterolLDL": 137.5175503762128,
         "CholesterolHDL": 25.482467035806813,
         "CholesterolTriglycerides": 313.66674876926953,
         "UPDRS": 58.99092096333794,
         "MoCA": 19.902233615718146,
         "FunctionalAssessment": 5.104914484020905,
         "Tremor": "0",
         "Rigidity": "1",
         "Bradykinesia": "1",
         "PosturalInstability": "0",
         "SpeechProblems": "0",
         "SleepDisorders": "1",
         "Constipation": "0"
        },
   "patient_id": 123
}
```

### Sending test example kinesis event

```bash
KINESIS_STREAM_INPUT=parkinson-input-stream
aws kinesis put-record \
   --stream-name ${KINESIS_STREAM_INPUT} \
   --partition-key 1 \
   --data "Hello, this is a test."
```

### Sending actual data

```bash
KINESIS_STREAM_INPUT=parkinson-input-stream
aws kinesis put-record \
   --stream-name ${KINESIS_STREAM_INPUT} \
   --partition-key 1 \
   --data '{
            "data": {
                  "Age": 67,
                  "Gender": "1",
                  "Ethnicity": "2",
                  "EducationLevel": "1",
                  "BMI": 24.77259403457728,
                  "Smoking": "0",
                  "AlcoholConsumption": 13.941385740391004,
                  "PhysicalActivity": 2.472534322357399,
                  "DietQuality": 9.593309739128369,
                  "SleepQuality": 6.060992120577725,
                  "FamilyHistoryParkinsons": "0",
                  "TraumaticBrainInjury": "0",
                  "Hypertension": "1",
                  "Diabetes": "0",
                  "Depression": "0",
                  "Stroke": "0",
                  "SystolicBP": 92,
                  "DiastolicBP": 60,
                  "CholesterolTotal": 193.1381868106296,
                  "CholesterolLDL": 137.5175503762128,
                  "CholesterolHDL": 25.482467035806813,
                  "CholesterolTriglycerides": 313.66674876926953,
                  "UPDRS": 58.99092096333794,
                  "MoCA": 19.902233615718146,
                  "FunctionalAssessment": 5.104914484020905,
                  "Tremor": "0",
                  "Rigidity": "1",
                  "Bradykinesia": "1",
                  "PosturalInstability": "0",
                  "SpeechProblems": "0",
                  "SleepDisorders": "1",
                  "Constipation": "0"
               },
            "patient_id": "39767a17-e85f-4655-81f4-2021c67f4e75"
         }'
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='parkinson-output-stream'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR --limit 100)

echo ${RESULT} | jq -r '.Records[-1].Data' | base64 --decode | jq
```

### Configure Enviromental Variables for Kinesis output stream

```bash
export PREDICTIONS_STREAM_NAME="kinesis-output-stream"
```

### Running the docker with Lambda and Kinesis

```bash
docker build -t parkinson-disease-prediction:latest .

docker run -it --rm \
    -p 8080:8080 \
    -e RUN_ID="${RUN_ID}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e PREDICTIONS_STREAM_NAME="${PREDICTIONS_STREAM_NAME}" \
    parkinson-disease-prediction:latest
```

### Publishing Docker images

Creating an ECR repo

```bash
aws ecr create-repository --repository-name parkinson-disease-prediction-model
```

Logging in

```bash
$(aws ecr get-login --no-include-email)
```

Pushing

```bash
REMOTE_URI="058264402883.dkr.ecr.eu-central-1.amazonaws.com/parkinson-disease-prediction-model"
REMOTE_TAG="v9"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="parkinson-disease-prediction:latest"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```