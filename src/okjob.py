import requests
from datetime import datetime
import json
import os
from constants import Constants
from logger import setup_logging, logging
from helpers import save_raw_api_data, load_raw_api_data, save_processed_data, merge_files, remove_files


def get_entries(amount, first=1, headers={}):
    """
    Get all pages in range

    Args:
        amount : int                    = number of entries to collect, it seems that the max amount is 926 - 1 (header) = 925 entries
        first (optional) : int          = first entry (always contains feature names)
        headers (optional) : dict       = headers for api request 
    
    Returns:
        None 
    """
    if amount < 1:
        raise ValueError(f"amount must be <= 1")
    save_raw_joblist(end=amount + 1 , headers=headers)    


def save_raw_joblist(start=1, end=20, subdir = Constants.DIR_NAME_OKJOB, headers={}):
    """
    Get okjob raw joblist by api call and save it in data/raw

    Args:
        start: str                  = minimun value = 1, first entry always contains the keys/header/schema
        end: str                    = number of job entries, first entry is no job entry see start
        subdir : str                = subfolder in data/raw to save results, default Constants.DIR_NAME_OKJOB
        headers (optional) : dict   = headers to send with api call

    Returns:
        None
    """

    response_data , response_code = get_raw_joblist(start=start, end=end, headers=headers)
    if response_code == 200:
        if subdir == '':
            subdir = Constants.DIR_NAME_OKJOB_NAME_MUSE                    # create a folder for each source 
        now = datetime.now().replace(microsecond=0)
        fname = f"okjob_raw_joblist.entires{str(start)}-{str(end)}.{now}.json"  # filename includes timestamp of request
        fname.replace(' ','_')                                  # no empty spaces in filename
        save_raw_api_data(fname, response_data, subdir)
    else:
        logging.debug(f"okjob.py: save_raw_joblist: no data to save")


def get_raw_joblist(start=1, end=2, headers={}):
    """
    Send api get request to load muse joblist

    Args:
        start: str       = minimun value = 1, first entry always contains the keys/header/schema
        end: str         = number of job entries, first entry is no job entry see start
        header : dict    = headers to send
    Returns:
        tupel : ( json data : str, response code : str) 
    """
    url = f"https://sheets.googleapis.com/v4/spreadsheets/1owGcfKZRHZq8wR7Iw6PVh6-ueR0weIVQMjxWW_0M6a8/values/Sheet1!A{start}:N{end}?key={Constants.OKJOB_API_KEY}"

    logging.debug(f"okjob.py: GET REQUEST API FOR: {url}, HEADERS: {headers}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.debug(f"okjob.py: {url}: CONNECTION SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    else:
        logging.error(f"okjob.py: {url}: CONNECTION NOT SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    return response.text, response.status_code



def proccess_raw_data(source_subdir=Constants.DIR_NAME_OKJOB, target_subdir=Constants.DIR_NAME_OKJOB, delete_processed = False, write_json=True, write_csv=True):
    """
    Extract information of all files in data/raw/<subfolder> and save them in data/processed
    
    Args:
        source_subdir : str                = subfolder in data/raw to load raw data, default Constants.DIR_NAME_MUSE
        target_subdir : str                = subfolder in data/processed to save processed data, default Constants.DIR_NAME_MUSE
        delete_processed (optional) : bool = should source file to be deleted ?       
        write_json (optional) : bool       = write file as json ?
        write_csv (optional) : bool        = write file as csv ?
    
    Returns:
        None
    """
    
    raw_api_data = load_raw_api_data(subdir=source_subdir)
    
    for tupel_entry in raw_api_data:
        fname, json_data = tupel_entry
        logging.debug(f"okjob.py: proccess_raw_data: process raw file {fname}")

        keys = json_data['values'][0]       # keys are in the first entry
        values = json_data['values'][1:]    # all other entries contain values

        # create dict
        json_dict_list = [dict(zip(keys, row)) for row in values]
        result_list = []
        for json_dict in json_dict_list: 
            # create id for entry
            id_entry = json_dict["LinkedIn-Job-Link"].split('-')[-1]
            try:
                json_dict["id"] = str(int(id_entry))
            except:
                logging.error(f"okjob.py: proccess_raw_data: cant cast id: {id_entry}")
                break
            
            # save full job description in subfolder
            # TODO: delete these files if no longer needed
            jobd_folder = os.path.join(Constants.PATH_DATA_PROCESSED, Constants.DIR_NAME_OKJOB, "full_job_description")
            
            if not os.path.exists(jobd_folder):
                logging.debug(f"okjob.py: proccess_raw_data: create job description folder: {jobd_folder}")
                os.makedirs(jobd_folder, exist_ok=True)
            jobd_fname = f"okjob_jobdesc_id={json_dict['id']}.html"
            job_full_path = os.path.join(jobd_folder, jobd_fname)
            with open(job_full_path, 'w') as f:            
                    f.write(json_dict["Job-Description"])
            json_dict["Job-Description"] = job_full_path
            result_list.append(json_dict)

        save_processed_data(result_list, fname, target_subdir, delete_source=delete_processed, write_json=write_json, write_csv=write_csv)


def merge_processed_files(prefix='okjob_proc', delete_source=False):
    """
    Merges processed single json and csv files into one big file
    Args:
        pefix : str             = files to merge must begin with prefix
        delete_soure : bool     = delete source files ?
    Returns:
        None
    """
    merge_files(Constants.DIR_NAME_OKJOB, prefix, delete_source=delete_source)


def remove_raw_data():
    """
    Remove raw data from data/raw/okjob.io, should be called before getting new raw data via api call

    Args:
        None
    
    Returns:
        None
    """
    raw2delete = []
    okjob_dir = os.path.join(Constants.PATH_DATA_RAW, Constants.DIR_NAME_OKJOB)

    if os.path.exists(okjob_dir):
        for entry in os.listdir(okjob_dir):
            if entry.endswith('.json') or entry.endswith('.csv'):
                raw2delete.append(os.path.join(okjob_dir, entry))
                
    remove_files(raw2delete)


if __name__ == "__main__":
    setup_logging()
    #job_list = get_raw_joblist(start=3,end=3)
    #print("Job list return length:", len(job_list[0]))
    #print(job_list[0])
    #save_raw_joblist(start=1, end=30)
    #for i in range(5):
    #    save_raw_joblist(i)
    #proccess_raw_data(delete_processed=False)
    #merge_processed_files(delete_source=True)
    remove_raw_data()