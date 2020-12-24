FROM python:3.7

RUN mkdir -p /app

RUN apt-get update && apt-get install screen

RUN pip install -r requirement.txt