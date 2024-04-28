#!/bin/bash

# create need folder structure just in case
mkdir -p ./data/logs/
mkdir -p ./data/raw/
mkdir -p ./data/processed/
mkdir -p ./data/model/

# for the presentation, create empty log files
touch ./data/logs/data_retrieval.log
touch ./data/logs/transform.log
touch ./data/logs/model_creation.log
touch ./data/logs/api.log

# set PIPELINE_ACTION for setup phase
export PIPELINE_ACTION="init"

# start database and initial data retrieval process
docker-compose up -d jobmarket_db jobmarket_data_retrieval --env PIPLINE_INIT=init --env s=371 --env e=392 --env l=10

# when data retrieval is complete, start transform
docker wait jobmarket_data_retrieval
docker-compose up -d jobmarket_transform

# when transform is complete, start model creation
docker wait jobmarket_transform
docker-compose up -d jobmarket_model

# when model creation is complete, start api
docker wait jobmarket_model
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