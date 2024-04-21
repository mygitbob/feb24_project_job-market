FROM python:3.9.5-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN pip install numpy==1.26.4 pandas==2.2.1 python-dateutil==2.9.0.post0 SQLAlchemy==2.0.29

RUN pip install psycopg2

RUN pip install spacy==3.7.4 spacy-legacy==3.0.12 spacy-loggers==1.0.5 && python -m spacy download en_core_web_sm

WORKDIR /transform_app/

RUN mkdir /transform_app/data/

COPY ./src/postgres/postgres_initdb.py /transform_app/
COPY ./src/postgres/postgres_create.py /transform_app/
COPY ./src/postgres/postgres_inserts.py /transform_app/
COPY ./src/postgres/check_dataframe.py /transform_app/
COPY ./src/logger/logger.py /transform_app/   
COPY ./src/transform/main.py /transform_app/
COPY ./src/transform/init.py /transform_app/
COPY ./src/transform/job_categories_and_skills.py /transform_app/
COPY ./src/transform/helpers.py /transform_app/
COPY ./src/transform/transform_reed.py /transform_app/


