#!/bin/bash

# check if database and api are still running and restart them if not
./restart_services.sh

# lead environment variables
source .env
# set PIPELINE_ACTION for update phase
export PIPELINE_ACTION="update"

# start data retrieval update process
docker-compose -d up jobmarket_db jobmarket_data_retrieval

# warte auf Abschluss der Datenabrufaktualisierung und starte dann die Transformation
docker wait jobmarket_data_retrieval
docker-compose -d up jobmarket_transform 

# warte auf Abschluss der Transformation und starte dann die Modellerstellung
docker wait jobmarket_transform
docker-compose -d up jobmarket_model