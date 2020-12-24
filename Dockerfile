FROM python:3.7

COPY . /app

WORKDIR /app

RUN apt-get update && apt-get install screen

RUN pip install -r requirement.txt

ENTRYPOINT ["python"]
CMD ["run.py"]