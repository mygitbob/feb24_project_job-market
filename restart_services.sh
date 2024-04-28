#!/bin/bash

# check if postgres and api are running, if not restart them

if ! docker-compose ps | grep -q 'jobmarket_db'; then
    echo "Restarting postgres container..."
    docker-compose  -d jobmarket_db --env-file .env up
else
    echo "Postgres container is running."
fi

if ! docker-compose ps | grep -q 'jobmarket_api'; then
    echo "Restarting api container..."
    docker-compose  -d jobmarket_api --env-file .env up
else
    echo "Api container is running."
fi
