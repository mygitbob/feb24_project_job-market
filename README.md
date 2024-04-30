# Datasientest Project: feb24_project_job-market

**TODO** Insert project description<br>

## Building the docker images
This section is for building and testing individual docker images/containers.<br>
To build them all in one step use the `docker-compose` command, see install instructions.<br>
For using the following commands you have to be in the project root folder.<br>
Create the required folder structure with:<br>
```bash
mkdir -p ./data/logs/
mkdir -p ./data/raw/
mkdir -p ./data/processed/
mkdir -p ./data/model/
```
### Setting up the database and network
Create the network (it´s briged by default)<br>
`docker network create jobmarket_net`<br>
<br>
Create the database:<br>
```bash
docker run --rm -d -p 5432:5432 
-e POSTGRES_PASSWORD=feb24 
--network jobmarket_net 
--name jobmarket_db  
-v ${PWD}/data/postgres:/var/lib/postgresql/data 
-v ${PWD}/src/postgres:/docker-entrypoint-initdb.d
postgres
``` 
This command uses the `create_databse.sql` script of the `./src/postgres` folder to create the database during its first start.
<br>
### Build the data_retrieval app

`docker build -t data_retrieval_app -f ./src/data_retrieval/Dockerfile .`<br>
Create a container to check if it works:<br>
`docker run --rm -it data_retrieval_app bash`<br>
### Test the data retireval app
Start the transformation app with the required configuration.<br>
```bash
docker run --rm -it 
-e PATH_DATA_RAW="/data_retrieval_app/data/raw" 
-e PATH_DATA_PROCESSED="/data_retrieval_app/data/processed" 
-e DIR_NAME_MUSE="muse.com" 
-e DIR_NAME_REED="reed.co.uk" 
-e KNOWN_CURRENCY="['$', '£', '€']" 
-e DIR_NAME_OKJOB="okjob.io" 
-e OKJOB_API_KEY="<API Key>" 
-e REED_API_KEY="<API Key>" 
-e API_VERSION_REED="1.0" 
-e LOGFILE=data/data_retrieval.log 
-v ${PWD}/data/:/data_retrieval_app/data/ 
--name jobmarket_data_retrieval data_retrieval_app
```
<br>
We can now use our data retrieval command:<br>

`python main.py -h`<br>

```
usage: main.py [-h] [-s START_INDEX] [-e END_INDEX] [-l SLEEP_TIME] {init,update}

Data retrieval tool that can perform initial data retrieval or an update ('init' or 'update')

positional arguments:
  {init,update}         data retrieval, can either do the initial data retrieval or and update ('init' or 'update')

optional arguments:
  -h, --help            show this help message and exit
  -s START_INDEX, --start START_INDEX
                        Start index for reed init
  -e END_INDEX, --end END_INDEX
                        End index for reed init
  -l SLEEP_TIME, --sleep SLEEP_TIME
                        Idle time for reed init
```

### Build the transform app
`docker build -t transform_app -f ./src/transform/Dockerfile .`<br>
<br>
Create a container and test it:<br>

`docker run --rm -it transform_app bash`<br>
<br>

### Test the transform app
Start the transformation app with the required configuration.<br>

```bash
docker run --rm -it 
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
transform_app bash
``` 
<br>

### Build the model app

`docker build -t model_app -f ./src/model_creation/Dockerfile .`<br>
<br>
Create a container and test it:<br>

`docker run --rm -it model_app bash`<br>
<br>

### Test the model app
Start the model app with the required configuration.<br>

```bash
docker run --rm -it 
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
model_app bash
``` 
### Build the api app
`build -t api_app -f ./src/api/Dockerfile .`<br>
Create a container and test it:<br>
`docker run --rm -it api_app bash`<br>
<br>

### Test the api app
Start the api app with the required configuration (use option `-d` if you don´t want to see the output):<br>

```bash
docker run --rm -it  -p 8000:8000 
-e PATH_MODEL="/api_app/data/model"  
-e POSTGRES_DBNAME="jobmarket"  
-e POSTGRES_USER="postgres"  
-e POSTGRES_PASSWORD="feb24"  
-e POSTGRES_HOST="jobmarket_db"  
-e POSTGRES_PORT=5432  
-e LOGFILE=data/api.log  
-e UVICORN_PORT=8000 
-v ${PWD}/data/:/api_app/data/  
--network jobmarket_net 
--name jobmarket_api api_app
``` 
<br>
You can now access the api via your browser and test the api:<br>
http://localhost:8000/docs <br>
<br>

## Install instructions
First you have to give the install/update scripts the permission to execute:

```bash
chmod +x  setup_jobmarket.sh
```
```bash
chmod +x  run_update_pipeline.sh
```
```bash
chmod +x  restart_services.sh
```
<br>
Next you have to run the  

`setup_jobmarket.sh`
This will create the required folder structure in the data folder,
create the jobmarket database and start the postgres container.
Then the initial ETL pipline will be run. The containers will started one after another. 
First the data retrieval, then the transform, which also stores the data in the jobmarket database.
The pipeline also includes the model training, which is done by the model container after transform has ended.
When the modles are created the api service is started.
Finally the script adds a cronjob for the `run_update_pipeline.sh` which will be stated every Sunday at 23.00.
<br>

`run_update_pipeline.sh` starts the data retrieval, tranform and create model services one after another.
They will download the newest data from the sources, transform and save the data and then create new models with the updated data.
<br>

`restart_services.sh` script can be used to restart the postgres and api service. These two services should be running all the time.
If the system will be rebooted the script can be used to restart them again. The `run_update_pipeline.sh` also uses thsi script to check
if the databse is availible and if not restart it.<br>

## Architecture
TODO

<br>
Postgres Schema
<br>
```mermaid
JOB-TITLE }|--|| JOB-OFFER : has
    JOB-OFFER |o--|{ JOB-TO-SKILLS : maps
    JOB-OFFER |o--|{ JOB-TO-CATEGORIES : maps
    JOB-OFFER ||--|{ CURRENCY : uses
    JOB-OFFER ||--|{ LOCATION : based-in
    JOB-OFFER ||--|{ DATA-SOURCE : sourced-from
    JOB-OFFER |o--|{ EXPERIENCE : requires
    JOB-TO-SKILLS }|--o| SKILL-LIST : includes
    JOB-TO-CATEGORIES }|--o| JOB-CATEGORY : includes    
    
    JOB-TITLE {
        int jt_id PK
        string name
        string unique_job_title UK
    }

    CURRENCY {
        int c_id PK
        string symbol
        string name
    }

    EXPERIENCE {
        int e_id PK
        string level
        string unique_experience UK
    }

    LOCATION {
        int l_id PK
        string country
        string region
        string city
        string city_district
        string area_code
        string state
        string unique_location_tuple UK
    }

    DATA-SOURCE {
        int ds_id PK
        string name
        string unique_data_source UK
    }

    SKILL-LIST {
        int sl_id PK
        string name
        string unique_skill_name UK
    }

    JOB-CATEGORY {
        int jc_id PK
        string name
        string unique_job_category UK
    }

    JOB-OFFER {
        int jo_id PK
        string source_id
        date published
        int salary_min
        int salary_max
        string joboffer_url
        int job_title_id FK
        int currency_id FK
        int location_id FK
        int data_source_id FK
        int experience_id FK
        string unique_data_source_id UK
        string unique_joboffer UK
    }

    JOB-TO-SKILLS {
        int job_id FK
        int skill_id FK
    }

    JOB-TO-CATEGORIES {
        int job_id FK
        int cat_id FK
    }
```