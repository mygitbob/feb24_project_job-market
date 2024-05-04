#!/bin/bash

# lead environment variables
source .env
# set PIPELINE_ACTION for setup phase
export PIPELINE_ACTION="init"

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

# start database
docker-compose up -d jobmarket_db

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

echo "Setup phase finished"

echo "Starting tests..."
ERROR_FILE="data/pytest_results.txt"

# tests should work, however if venv isn´t activated it is possible that configuration for pytest does not work (anaconda install for example)
# test can be done manually after install

#if pytest -v tests/ > $ERROR_FILE 2>&1; then
#    echo "All tests ran successfully, adding cronjob"
#else
#    echo "Error: one or more tests did not succeed. Details can be found in the file $ERROR_FILE"
#    exit 1
#fi

# add cronjob
# get absolut path to update script
SCRIPT_PATH=$(readlink -f ./run_update_pipeline.sh)
# create job that runs our script every sunday at 23.00
CRON_COMMAND="0 23 * * 0 bash $SCRIPT_PATH"
# create entry in crontab
echo "$CRON_COMMAND" | crontab -

echo "Cron job for update pipline created"