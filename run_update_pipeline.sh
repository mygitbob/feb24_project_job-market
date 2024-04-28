#!/bin/bash

# check if database and api are still running and restart them if not
./restart_services.sh

# set PIPELINE_ACTION for update phase
export PIPELINE_ACTION="update"

# start data retrieval update process
docker-compose -d jobmarket_db jobmarket_data_retrieval --env-file .env up

# warte auf Abschluss der Datenabrufaktualisierung und starte dann die Transformation
docker wait jobmarket_data_retrieval
docker-compose -d jobmarket_transform --env-file .env up

# warte auf Abschluss der Transformation und starte dann die Modellerstellung
docker wait jobmarket_transform
docker-compose -d jobmarket_model --env-file .env up