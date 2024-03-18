    
import requests
from datetime import datetime
import json
import os
from constants import Constants
from logger import setup_logging, logging
from helpers import save_raw_api_data, load_raw_api_data, save_processed_data, merge_files, remove_files


def get_entries(headers={}, parameters={}):
    """
    Get all jon entries

    Args:
        amount : int                    = number of entries to collect, it seems that the max amount is 926 - 1 (header) = 925 entries
        first (optional) : int          = first entry (always contains feature names)
        headers (optional) : dict       = headers for api request 
    
    Returns:
        None 
    """
    
    save_raw_joblist(headers=headers, parameters=parameters)    


def save_raw_joblist(subdir = '', headers={}, parameters={}):
    """
    Get reed raw joblist by api call and save it in data/raw

    Args:
        subdir : str                = subfolder in data/raw to save results, if empty use Constants.DIR_NAME_REED
        headers (optional) : dict   = headers to send with api call
        parameters (optional) : dict    = arguments for url query

    Returns:
        None
    """

    response_data , response_code = get_raw_joblist(headers=headers, parameters=parameters)
    if response_code == 200:
        if subdir == '':
            subdir = Constants.DIR_NAME_REED                    # create a folder for each source 
        now = datetime.now().replace(microsecond=0)
        fname = f"reed_raw_joblist.{now}.json"                  # filename includes timestamp of request
        fname.replace(' ','_')                                  # no empty spaces in filename
        save_raw_api_data(fname, response_data, subdir)
    else:
        logging.debug(f"reed.py: save_raw_joblist: no data to save")


def get_raw_joblist(headers={}, parameters={}):
    """
    Send api get request to load reed joblist

    Args:
        parameters (optional) : dict    = arguments for url query
        headers (optional) : dict       = headers to send with api call

        Example query string: "?keywords=accountant&location=london"
    Returns:
        tupel : ( json data : str, response code : str) 
    """
    url = f"https://www.reed.co.uk/api/{Constants.API_VERSION_REED}/search"
    
    if parameters:
        query = "?"
        for key, value in parameters.items():
            query += key + '=' + value + '&'
        url += query[:-1]   # exclude final & 

    # we have to do basic authentication
    auth_header = requests.auth.HTTPBasicAuth(Constants.REED_API_KEY, '')
    
    logging.debug(f"reed.py: GET REQUEST API FOR: {url}, AUTH: {auth_header} HEADERS: {headers}")
    response = requests.get(url, auth=auth_header, headers=headers)

    if response.status_code == 200:
        logging.debug(f"reed.py: {url}: CONNECTION SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    else:
        logging.error(f"reed.py: {url}: CONNECTION NOT SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    return response.text, response.status_code



def proccess_raw_data(source_subdir=Constants.DIR_NAME_REED, target_subdir=Constants.DIR_NAME_REED, delete_processed = False, write_json=True, write_csv=True):
    """
    Extract information of all files in data/raw/<subfolder> and save them in data/processed
    
    Args:
        source_subdir : str                = subfolder in data/raw to load raw data, default Constants.DIR_NAME_REED
        target_subdir : str                = subfolder in data/processed to save processed data, default Constants.DIR_NAME_REED
        delete_processed (optional) : bool = should source file to be deleted ?       
        write_json (optional) : bool       = write file as json ?
        write_csv (optional) : bool        = write file as csv ?
    
    Returns:
        None
    """
    
    raw_api_data = load_raw_api_data(subdir=source_subdir)
    
    for tupel_entry in raw_api_data:
        fname, json_data = tupel_entry
        logging.debug(f"reed.py: proccess_raw_data: process raw file {fname}")

        job_entries = json_data['results']
        if job_entries:
            save_processed_data(job_entries, fname, target_subdir, delete_source=delete_processed, write_json=write_json, write_csv=write_csv)   
        else:
            logging.error(f"reed.py: result list empty for file: {fname}")


def merge_processed_files(prefix='reed_proc', delete_source=False):
    """
    Merges processed single json and csv files into one big file
    Args:
        pefix : str             = files to merge must begin with prefix
        delete_soure : bool     = delete source files ?
    Returns:
        None
    """
    merge_files(Constants.DIR_NAME_REED, prefix, delete_source=delete_source)


def remove_raw_data():
    """
    Remove raw data from data/raw/reed.co.uk, should be called before getting new raw data via api call

    Args:
        None
    
    Returns:
        None
    """
    raw2delete = []
    reed_dir = os.path.join(Constants.PATH_DATA_RAW, Constants.DIR_NAME_REED)

    if os.path.exists(reed_dir):
        for entry in os.listdir(reed_dir):
            if entry.endswith('.json') or entry.endswith('.csv'):
                raw2delete.append(os.path.join(reed_dir, entry))
                
    remove_files(raw2delete)


if __name__ == "__main__":
    setup_logging()
    #job_list = get_raw_joblist(parameters={"resultsToSkip":"200"})
    #print("Job list return length:", len(job_list[0]))
    #print(job_list[0])
    #save_raw_joblist(parameters={"keywords":"accountant","location":"london"})
    #save_raw_joblist()
    #save_raw_joblist(parameters={"resultsToSkip":"200"})
    proccess_raw_data(delete_processed=False)
    #merge_processed_files(delete_source=True)
    #remove_raw_data()