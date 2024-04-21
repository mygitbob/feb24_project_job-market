FROM python:3.9.5-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN pip install numpy==1.26.4 pandas==2.2.1 python-dateutil==2.9.0.post0 SQLAlchemy==2.0.29

RUN pip install psycopg2

WORKDIR /transform_app/

RUN mkdir /transform_app/data/

COPY ./postgres/postgres_initdb.py /transform_app/
COPY ./postgres/postgres_create.py /transform_app/
COPY ./postgres/postgres_inserts.py /transform_app/
COPY ./postgres/check_dataframe.py /transform_app/
COPY ./logger/logger.py /transform_app/   
COPY ./transform/main.py /transform_app/
COPY ./transform/init.py /transform_app/
COPY ./transform/job_categories_and_skills.py /transform_app/
COPY ./transform/helpers.py /transform_app/
COPY ./transform/transform_reed.py /transform_app/


