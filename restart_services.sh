#!/bin/bash

# check if postgres and api are running, if not restart them

# lead environment variables
source .env

if ! docker-compose ps | grep -q 'jobmarket_db'; then
    echo "Restarting postgres container..."
    docker-compose -d up jobmarket_db
else
    echo "Postgres container is running."
fi

if ! docker-compose ps | grep -q 'jobmarket_api'; then
    echo "Restarting api container..."
    docker-compose -d up jobmarket_api
else
    echo "Api container is running."
fi
