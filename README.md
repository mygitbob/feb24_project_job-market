# Datasientest Project: feb24_project_job-market

**TODO**
write project description
write install / how to use description

## Building the docker images
### data_retrieval_app
**we first have to create the directory structure before starting the container**, this should work for now since it is already created but we have to think about it.<br>
From the `src` folder use the command:<br>
`docker build -t data_retrieval_app -f ./data_retrieval/Dockerfile .`<br>
Create a container and test it:<br>
`docker run --rm -it data_retrieval_app bash`<br>
<br>
Test for windows<br>
**you have to be in the `src` folder !**<br>
`docker run --rm -it -e PATH_DATA_RAW="/data_retrieval_app/data/raw_data" -e PATH_DATA_PROCESSED="/data_retrieval_app/data/processed_data" -e DIR_NAME_MUSE="muse.com" -e DIR_NAME_REED="reed.co.uk" -e KNOWN_CURRENCY="['$', '£', '?']" -e DIR_NAME_OKJOB="okjob.io" -e OKJOB_API_KEY="AIzaSyDErRezqW2klWRYKwQkzuOIMGJ5AeD5GSY" -e REED_API_KEY="52f1eba3-39f1-4ee8-bc36-26140b349e67" -e API_VERSION_REED="1.0" -v ${PWD}/../docker/persistant_data/:/data_retrieval_app/data/ data_retrieval_app bash`<br>
<br>
<br>
We can now use your data retrieval command:<br>
`python main.py`<br>
usage: main.py [-h] [-s START_INDEX] [-e END_INDEX] [-l SLEEP_TIME] {init,update}<br>
<br>
Data retrieval tool that can perform initial data retrieval or an update ('init' or 'update')<br>
<br>
positional arguments:<br>
  {init,update}         datat retrieval, can either do the initial data retrieval or and update ('init' or 'update')
<br>
optional arguments:<br>
  -h, --help            show this help message and exit<br>
  -s START_INDEX, --start START_INDEX<br>
                        Start index for reed init<br>
  -e END_INDEX, --end END_INDEX<br>
                        End index for reed init<br>
  -l SLEEP_TIME, --sleep SLEEP_TIME<br>
                        Idle time for reed init<br>
<br>
### transform_app
From the `src` use the command:<br>
TODO
