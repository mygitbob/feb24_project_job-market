#!/bin/bash

# check if database and api are still running and restart them if not
./restart_services.sh

# start data retrieval update process
docker-compose up -d jobmarket_db jobmarket_data_retrieval --env PIPELINE_ACTION=update

# warte auf Abschluss der Datenabrufaktualisierung und starte dann die Transformation
docker wait jobmarket_data_retrieval
docker-compose up -d jobmarket_transform

# warte auf Abschluss der Transformation und starte dann die Modellerstellung
docker wait jobmarket_transform
docker-compose up -d jobmarket_model