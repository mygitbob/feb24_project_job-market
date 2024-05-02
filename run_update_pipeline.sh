#!/bin/bash

# check if database and api are still running and restart them if not
bash ./restart_services.sh 

# load environment variables
source .env
# set PIPELINE_ACTION for update phase
export PIPELINE_ACTION="update"

# delete old data if anything is left
rm -rf ./data/processed/muse.com/merged/* 2>/dev/null
rm -rf ./data/processed/okjob.io/merged/* 2>/dev/null
rm -rf ./data/processed/okjob.io/full_job_description/* 2>/dev/null
rm -rf ./data/processed/reed.co.uk/merged/* 2>/dev/null

docker-compose up -d jobmarket_db jobmarket_data_retrieval

docker wait jobmarket_data_retrieval_container
docker-compose up -d jobmarket_transform 

docker wait jobmarket_transform_container
docker-compose up -d jobmarket_model