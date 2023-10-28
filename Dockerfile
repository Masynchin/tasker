FROM python:3.11.6-slim-bookworm

RUN apt-get update && apt-get install build-essential -y

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .
