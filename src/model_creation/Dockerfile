FROM python:3.9.5-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN pip install numpy==1.26.4 pandas==2.2.1 python-dateutil==2.9.0.post0 SQLAlchemy==2.0.29

RUN pip install scikit-learn==1.4.2


WORKDIR /model_app/

RUN mkdir /model_app/data/

COPY ./src/postgres/postgres_initdb.py /model_app/
COPY ./src/postgres/postgres_queries.py /model_app/
COPY ./src/logger/logger.py /model_app/   
COPY ./src/model_creation/main.py /model_app/
COPY ./src/model_creation/init.py /model_app/
COPY ./src/model_creation/mlmodel.py /model_app/


