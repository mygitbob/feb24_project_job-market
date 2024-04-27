# Datasientest Project: feb24_project_job-market

**TODO**
fix bug when database connection cant be established:
`UnboundLocalError: local variable 'conn' referenced before assignment`<br>
write project description<br>
write install / how to use description<br>

# Building the docker images
## data_retrieval app
**we first have to create the directory structure before starting the container**, this should work for now since it is already created but we have to think about it.<br>
From the root folder use the command:<br>
`docker build -t data_retrieval_app -f ./src/data_retrieval/Dockerfile .`<br>
Create a container and test it:<br>
`docker run --rm -it data_retrieval_app bash`<br>
<br>
We can now use our data retrieval command:<br>
`python main.py -h`<br>
```
usage: main.py [-h] [-s START_INDEX] [-e END_INDEX] [-l SLEEP_TIME] {init,update}

Data retrieval tool that can perform initial data retrieval or an update ('init' or 'update')

positional arguments:
  {init,update}         datat retrieval, can either do the initial data retrieval or and update ('init' or 'update')

optional arguments:
  -h, --help            show this help message and exit
  -s START_INDEX, --start START_INDEX
                        Start index for reed init
  -e END_INDEX, --end END_INDEX
                        End index for reed init
  -l SLEEP_TIME, --sleep SLEEP_TIME
                        Idle time for reed init
```
### test the data retireval app
**you have to be in the project root folder !**<br>
<br>
`docker run --rm -it 
-e PATH_DATA_RAW="/data_retrieval_app/data/raw" 
-e PATH_DATA_PROCESSED="/data_retrieval_app/data/processed" 
-e DIR_NAME_MUSE="muse.com" 
-e DIR_NAME_REED="reed.co.uk" 
-e KNOWN_CURRENCY="['$', '£', '€']" 
-e DIR_NAME_OKJOB="okjob.io" 
-e OKJOB_API_KEY="AIzaSyDErRezqW2klWRYKwQkzuOIMGJ5AeD5GSY" 
-e REED_API_KEY="52f1eba3-39f1-4ee8-bc36-26140b349e67" 
-e API_VERSION_REED="1.0" 
-e LOGFILE=data/data_retrieval.log 
-v ${PWD}/data/:/data_retrieval_app/data/ 
--name jobmarket_data_retrieval
data_retrieval_app bash`
<br>
<br>

## transform app
From the root folder use the command:<br>
`docker build -t transform_app -f ./src/transform/Dockerfile .`<br>

Create a container and test it:<br>
`docker run --rm -it transform_app bash`<br>

We can now use our transformation command:<br>
`python main.py`<br>

### test the transform app
#### setting up the database and network
create a network (it´s briged by default)<br>
`docker network create jobmarket_net`<br>
<br>
create the database, use `create_database.sql` from `src/postgres` folder<br>
start postgres with default database:<br>
`docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=feb24 --network jobmarket_net --name jobmarket_db -d -v ${PWD}/data/postgres:/var/lib/postgresql/data postgres`<br>
create database jobmarket and tables<br>
`psql -U postgres -f ./src/postgres/create_database.sql`<br>
for windows, enter ` psql -U postgres -f .\src\postgres\create_databse.sql`<br> 

#### start the transform app
Start the transformation app with the required configuration.<br>
**you have to be in the project root folder !**<br>
<br>
`docker run --rm -it 
-e PATH_DATA_PROCESSED="/transform_app/data/processed" 
-e DIR_NAME_MUSE="muse.com/merged" 
-e DIR_NAME_REED="reed.co.uk/merged" 
-e DIR_NAME_OKJOB="okjob.io/merged" 
-e POSTGRES_DBNAME="jobmarket" 
-e POSTGRES_USER="postgres" 
-e POSTGRES_PASSWORD="feb24" 
-e POSTGRES_HOST="jobmarket_db" 
-e POSTGRES_PORT=5432 
-e LOGFILE=data/transform.log 
-v ${PWD}/data/:/transform_app/data/ 
--network jobmarket_net
--name jobmarket_transform
transform_app bash`

## model app
From the root folder use the command:<br>
`docker build -t model_app -f ./src/model_creation/Dockerfile .`<br>

Create a container and test it:<br>
`docker run --rm -it model_app bash`<br>

We can now use our transformation command:<br>
`python main.py`<br>

### test the model app
#### setting up the database and network
see transform app<br>
<br>
#### run model app
start postgres:<br>
`docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=feb24 --network jobmarket_net --name jobmarket_db -d postgres`<br>
<br>
Start the model app with the required configuration.<br>
**you have to be in the project root folder !**<br>
<br>
`docker run --rm -it 
-e PATH_MODEL="/model_app/data/model" 
-e POSTGRES_DBNAME="jobmarket" 
-e POSTGRES_USER="postgres" 
-e POSTGRES_PASSWORD="feb24" 
-e POSTGRES_HOST="jobmarket_db" 
-e POSTGRES_PORT=5432 
-e LOGFILE=data/model_creation.log 
-v ${PWD}/data/:/model_app/data/ 
--network jobmarket_net
--name jobmarket_model
model_app bash`
## api app
### build api app
From the root folder use the command:<br>
`build -t api_app -f ./src/api/Dockerfile .`

### test api app
Remeber, start the databse first ;)<br>
Start the container (can be done with `-d` if you don´t want to see the output):<br>
`docker run --rm -it  -p 8000:8000 -e PATH_MODEL="/api_app/data/model"  -e POSTGRES_DBNAME="jobmarket"  -e POSTGRES_USER="postgres"  
-e POSTGRES_PASSWORD="feb24"  -e POSTGRES_HOST="jobmarket_db"  -e POSTGRES_PORT=5432  -e LOGFILE=data/api.log  
-e UVICORN_PORT=8000 -v ${PWD}/data/:/api_app/data/  --network jobmarket_net --name jobmarket_api api_app`
<br>
You can now access the api via your browser and test the api:<br>
`http://localhost:8000/docs`

## How will our services interact/ be setup

I have identified 2 ways how we have to start our services, each of the phases will have its own docker-compose file:

1.) setup - this happens only once, it is the "installation phase"
- run script that creates the needed folder structure for the persitant folders of our containers
- start the databse container and create the jobmarket database
- run the pipeline: initial data retrieval (here we get as much data as we can/like) 
-> transform the initial data and storing in database
-> train the model for the first time
- start api service
The databse and the api service will be running forever and will never stop

2.) run the update pipeline, this can be initiated by a cronjob (no cronjob for windows, has to be linux or mac)
- start data retrieval update -> transformation of new data-> model retraining

This is an example of 3 containers that will be startetd one after another
We need this for the update pipline
data retrieval update -> new data transformation and storing in database -> model retraining

can be done with a docker-compose like this:

services:
  first_container:
    image: first_image
    restart: "no"  

  second_container:
    image: second_image
    restart: "no"
    depends_on:
      - first_container  
    
  third_container:
    image: third_image
    restart: "no"
    depends_on:
      - second_container  

So we have to start our services in 3 modes:
1. Initial setup and data collection:
  - create folder structure
  - start database service and create the jobmarket db, the database service has to be rujning all the time and never stops
  - make initial data retrieval -> start data retrieval app , run init and stop it after its done
  - transform initial data -> start transform app after data retrieval app has ended, transform data and then stop it
  - create initial models -> start model app after transform app is finished, create models and stop it
  - start api server, this also keeps running and never stops
2. Update pipeline, run these apps as decribed above:
  - start retrieval update, run update and stop
  - start transform, make transformation and stop
  - start model, create models and stop
3. mechanism to restart the services that should keep running:
  - (re-)start database service
  - (re-)start api server, database server must be running !
  