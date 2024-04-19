# Datasientest Project: feb24_project_job-market

**TODO**
write project description
write install / how to use description

## Building the docker images
### data_retrieval_app
**we first have to create the directory structure before starting the container**
From the `src` use the command:
`docker build -t data_retrieval_app -f ./data_retrieval/Dockerfile .`
Create a container and test it:
`docker run --rm -it data_retrieval_app bash`

Test for windows
`docker run --rm -it -e PATH_DATA_RAW="/data_retrieval_app/data/raw_data" -e PATH_DATA_PROCESSED="/data_retrieval_app/data/processed_data" -e DIR_NAME_MUSE="muse.com" -e DIR_NAME_REED="reed.co.uk" -e KNOWN_CURRENCY="['$', '£', '?']" -e DIR_NAME_OKJOB="okjob.io" -e OKJOB_API_KEY="AIzaSyDErRezqW2klWRYKwQkzuOIMGJ5AeD5GSY" -e REED_API_KEY="52f1eba3-39f1-4ee8-bc36-26140b349e67" -e API_VERSION_REED="1.0" -v ${PWD}/../docker/persistant_data/data/data_retrieval:/data_retrieval_app/data/ data_retrieval_app bash`

We can now use your data retrieval command:
`python main.py`
`usage: main.py [-h] [-s START_INDEX] [-e END_INDEX] [-l SLEEP_TIME] {init,update}

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
                        Idle time for reed init`

### transform_app
From the `src` use the command:
