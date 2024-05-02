#!/bin/bash

# create need folder structure just in case
mkdir -p ./data/logs/
mkdir -p ./data/raw/
mkdir -p ./data/processed/
mkdir -p ./data/model/
mkdir -p ./data/postgres/

# for the presentation, create empty log files
touch ./data/logs/data_retrieval.log
touch ./data/logs/transform.log
touch ./data/logs/model_creation.log
touch ./data/logs/api.log

# lead environment variables
source .env

# start database
docker-compose up -d jobmarket_db

# set PIPELINE_ACTION for setup phase
export PIPELINE_ACTION="init"
# start initial data retrieval process
docker-compose up -d jobmarket_data_retrieval

# when data retrieval is complete, start transform
docker wait jobmarket_data_retrieval_container
docker-compose up -d jobmarket_transform 

# when transform is complete, start model creation
docker wait jobmarket_transform_container
docker-compose up -d jobmarket_model

# when model creation is complete, start api
docker wait jobmarket_model_container
docker-compose up -d jobmarket_api

echo "setup phase finished"

# add cronjob
# get absolut path to update script
SCRIPT_PATH=$(readlink -f ./run_update_pipeline.sh)
# create job that runs our script every sunday at 23.00
CRON_COMMAND="0 23 * * 0 $SCRIPT_PATH"
# create entry in crontab
echo "$CRON_COMMAND" | crontab -

echo "cron job for update pipline created"