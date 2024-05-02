#!/bin/bash

# check if database and api are still running and restart them if not
bash ./restart_services.sh 

# lead environment variables
source .env
# set PIPELINE_ACTION for update phase
export PIPELINE_ACTION="update"

# start data retrieval update process
docker-compose up -d jobmarket_db jobmarket_data_retrieval

# warte auf Abschluss der Datenabrufaktualisierung und starte dann die Transformation
docker wait jobmarket_data_retrieval_container
docker-compose up -d jobmarket_transform 

# warte auf Abschluss der Transformation und starte dann die Modellerstellung
docker wait jobmarket_transform_container
docker-compose up -d jobmarket_model