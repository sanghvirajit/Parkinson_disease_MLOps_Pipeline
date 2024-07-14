FROM python:3.9.7-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY [ "model.py", "./" ]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
