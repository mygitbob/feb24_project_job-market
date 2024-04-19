FROM python:3.9.5-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN pip install numpy==1.26.4 pandas==2.2.1 python-dateutil==2.9.0.post0 beautifulsoup4==4.12.3 \
                certifi==2024.2.2 charset-normalizer==3.3.2 greenlet==3.0.3 idna==3.6 lxml==5.1.0

RUN pip install pytz==2024.1 requests==2.31.0 six==1.16.0 soupsieve==2.5 typing_extensions==4.11.0 \
                tzdata==2024.1 urllib3==2.2.1

WORKDIR /data_retrieval_app/

RUN mkdir /data_retrieval_app/data/

COPY ./data_retrieval/helpers.py /data_retrieval_app/
COPY ./data_retrieval/muse.py /data_retrieval_app/
COPY ./data_retrieval/okjob.py /data_retrieval_app/
COPY ./data_retrieval/reed_locations.py /data_retrieval_app/
COPY ./data_retrieval/reed.py /data_retrieval_app/
COPY ./data_retrieval/init.py /data_retrieval_app/
COPY ./data_retrieval/main.py /data_retrieval_app/
COPY ./logger/logger.py /data_retrieval_app/   


