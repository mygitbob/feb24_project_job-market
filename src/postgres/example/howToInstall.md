### Get postgres image
`docker pull postgres`

### Setup Postgres & start container
`docker run --name postgres_dummy -e POSTGRES_PASSWORD=dummy -d postgres`

#### Starting Container only 
`docker start postgres_dummy`

### Log into pqsl and create database
`docker exec -it postgres_dummy psql -U postgres`
#### List all databases in psql
`\l`
#### Connect to database in psql
`\c <name of db>`
#### Create new database (do this before running the scripts)
`CREATE DATABASE dummy_db;`
You can now connect to it via `\c dummy`
#### List all tables of the database dummy
```
SELECT table_name FROM information_schema.tables 
WHERE table_schema =  'public'  
AND table_catalog =  'dummy_db';
```
Should be empty at the time of creation ;)
### Copy the sql scripts into the container
In this example they are copied in the root dir, should not be done in the project
```
docker cp create_dummy_db.sql postgres_dummy:/create_dummy_db.sql
docker cp populate_dummy_db.sql postgres_dummy:/populate_dummy_db.sql
```
### Execute the scripts, create must be executed before populate !
```
docker exec -it postgres_dummy psql -U postgres -d dummy_db -f /create_dummy_db.sql
docker exec -it postgres_dummy psql -U postgres -d dummy_db -f /populate_dummy_db.sql
```

The scripts show a way how to insert data. I made it simple step by step. This can be done better
but would get more complicated. For example I fist enter the data to the fact table and afterwards I update 
the fact table with table with the foreign key of dim1. This could be done as one step.