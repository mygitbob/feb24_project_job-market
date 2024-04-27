FROM python:3.9.5-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN pip install numpy==1.26.4 pandas==2.2.1 python-dateutil==2.9.0.post0 SQLAlchemy==2.0.29

RUN pip install spacy==3.7.4 spacy-legacy==3.0.12 spacy-loggers==1.0.5 && python -m spacy download en_core_web_sm

RUN pip install psycopg2

RUN pip install uvicorn==0.29.0 joblib==1.4.0 scikit-learn==1.4.2

RUN pip install fastapi==0.110.2

WORKDIR /api_app/

RUN mkdir /api_app/data/

COPY ./src/postgres/postgres_initdb.py /api_app/
COPY ./src/postgres/postgres_queries.py /api_app/
COPY ./src/logger/logger.py /api_app/   
COPY ./src/api/main.py /api_app/
COPY ./src/api/init.py /api_app/
COPY ./src/api/routes.py /api_app/
COPY ./src/api/api_types.py /api_app/
COPY ./src/api/start_uvicorn.sh /api_app/
RUN chmod +x /api_app/start_uvicorn.sh

EXPOSE $UVICORN_PORT

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $UVICORN_PORT --reload"]