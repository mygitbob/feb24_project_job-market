#!/bin/bash

# start server 
clear
echo "Starting uvicorn"
nohup uvicorn main:app --reload --port $UVICORN_PORT 