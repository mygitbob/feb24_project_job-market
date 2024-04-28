#!/bin/bash

# check if postgres and api are running, if not restart them

if ! docker-compose ps | grep -q 'jobmarket_db'; then
    echo "Restarting postgres container..."
    docker-compose up -d jobmarket_db
else
    echo "Postgres container is running."
fi

if ! docker-compose ps | grep -q 'jobmarket_api'; then
    echo "Restarting api container..."
    docker-compose up -d jobmarket_api
else
    echo "Api container is running."
fi
