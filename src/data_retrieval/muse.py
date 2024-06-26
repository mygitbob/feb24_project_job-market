import requests
from datetime import datetime
import re
import os

from logger import logging
from init import DIR_NAME_MUSE, KNOWN_CURRENCY, PATH_DATA_RAW

from helpers import save_raw_api_data, load_raw_api_data, save_processed_data, merge_files, remove_files


def save_raw_joblist(page=0, subdir='', headers={}):
    """
    Get muse raw joblist by api call and save it in data/raw

    Args:
        page: str                   = page number to load, MAX VALUE IS 99
        subdir (optional) : str     = subfolder in data/raw to save results, if empty use Constants.DIR_NAME_MUSE
        headers (optional) : dict   = headers to send with api call

    Returns:
        None
    """
    if page > 99:
        logging.debug(
            f"save_raw_joblist: page number too high: {page}")
        return
    response_data, response_code = get_raw_joblist(page, headers)
    if response_code == 200:
        if subdir == '':
            # create a folder for each source
            subdir = DIR_NAME_MUSE
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # filename includes timestamp of request
        fname = f"muse_raw_joblist.page{str(page)}.{now}.json"
        # no empty spaces in filename
        fname.replace(' ', '_')
        save_raw_api_data(fname, response_data, subdir)
    else:
        logging.debug(f"save_raw_joblist: no data to save")


def get_raw_joblist(page, headers={}):
    """
    Send api get request to load muse joblist

    Args:
        page: str        = page number to load, MAX VALUE IS 99
        header : dict    = headers to send
    Returns:
        tupel : ( json data : str, response code : str) 
    """
    # TODO: register muse api key
    # url = f"https://www.themuse.com/api/public/jobs?api_key={Constants.MUSE_API_KEY}&page={page}"
    url = f"https://www.themuse.com/api/public/jobs?page={page}"

    logging.debug(f"GET REQUEST API FOR: {url}, HEADERS: {headers}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.debug(
            f"{url}: CONNECTION SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    else:
        logging.error(
            f"{url}: CONNECTION NOT SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    return response.text, response.status_code


def process_raw_data(source_subdir=DIR_NAME_MUSE, target_subdir=DIR_NAME_MUSE, delete_processed=False, write_json=True, write_csv=True):
    """
    Extract information from all files or a specific file from data/raw/<subfolder> and save them in data/processed
    For exact data points see code below

    Args:
        source_subdir : str                = subfolder in data/raw to load raw data, default Constants.DIR_NAME_MUSE
        target_subdir : str                = subfolder in data/processed to save processed data, default Constants.DIR_NAME_MUSE
        delete_processed (optional) : bool = should source file to be deleted ?       
        write_json (optional) : bool       = write file as json ?
        write_csv (optional) : bool        = write file as csv ?

    Returns:
        None
    """
    data2process = load_raw_api_data(subdir=source_subdir)
    for d2p in data2process:
        fname, data = d2p
        logging.debug(f"process_raw_data: process raw file {fname}")
        all_entries = []
        if 'results' not in data:
            logging.error(
                f"process_raw_data: no entry results for {fname}")
            break
        job_results = data['results']
        for job_result in job_results:
            job_entry = {}
            job_entry["job_title"] = job_result["name"].strip()
            job_entry["min_salary"], job_entry["max_salary"], job_entry['currency'] = extract_salary(
                job_result["contents"])
            job_entry["skills"] = extract_skills(job_result["contents"])
            job_entry["publication_date"] = job_result["publication_date"].strip()
            job_entry["id"] = str(job_result["id"]).strip()
            job_entry["location"] = job_result["locations"]
            job_entry["job_categories"] = job_result["categories"]
            # TODO: check html
            job_entry["experience"] = job_result["levels"][0]["short_name"].strip()
            job_entry["html_link"] = job_result["refs"]["landing_page"].strip()
            # not sure what this means
            job_entry["type"] = job_result["type"].strip()
            job_entry["company_name"] = job_result["company"]["name"].strip()
            job_entry["company_id"] = str(job_result["company"]["id"]).strip(
            )                           # muse company id
            # name of data source
            job_entry["source"] = "muse.com"
            job_entry["created"] = datetime.now().strftime(
                "%Y-%m-%d_%H:%M:%S")       # date when the script creates this entry
            # TODO: try to get how many hours to work
            all_entries.append(job_entry)    # save job entry
        save_processed_data(all_entries, fname, target_subdir,
                            delete_source=delete_processed, write_json=write_json, write_csv=write_csv)


def extract_salary(html_text):
    """
    Extracts salary information, its possible that nothing will be found

    Args:
        html_source: str    = html code of the job description 

    Returns:
            min_nr : float, max_nr : float, currency : str = $ | £ | € | NOT_FOUND
        OR 
            NOT_FOUND, NOT_FOUND, NOT_FOUND
    """
    pattern = rf'<br>The typical pay range for this role is:<br><br>(.*?)<br>'
    matches = re.search(pattern, html_text)

    if matches:
        currency = matches.group(1).strip()[0]
        if currency not in KNOWN_CURRENCY:
            currency = "_UNKOWN_"
        try:
            min_nr = matches.group(1).split('-')[0].strip()[1:]
            max_nr = matches.group(1).split('-')[1].strip()[1:]
        except:
            min_nr = max_nr = currency = "_NOT_FOUND_"
    else:
        min_nr = max_nr = currency = "_NOT_FOUND_"
    return min_nr, max_nr, currency


def extract_skills(html_text):
    """
    Extracts information on job skills , returns empty list when nothing is found

    Args:
        html_source: str    = html code of the job description 

    Returns:
            skills : list[ str ] | []

    """
    # TODO: implement
    return []


def merge_processed_files(prefix='muse_proc', delete_source=False):
    """
    Merges processed single json and csv files into one big file
    Args:
        pefix : str             = files to merge must begin with prefix
        delete_soure : bool     = delete source files ?
    Returns:
        None
    """
    merge_files(DIR_NAME_MUSE, prefix, delete_source=delete_source)


def remove_raw_data():
    """
    Remove raw data from data/raw/muse.com, should be called before getting new raw data via api call

    Args:
        None

    Returns:
        None
    """
    raw2delete = []
    muse_dir = os.path.join(PATH_DATA_RAW, DIR_NAME_MUSE)

    if os.path.exists(muse_dir):
        for entry in os.listdir(muse_dir):
            if entry.endswith('.json') or entry.endswith('.csv'):
                raw2delete.append(os.path.join(muse_dir, entry))

    remove_files(raw2delete)


def get_all_source_data(start=0, end=99, headers={}):
    """
    Get all pages in range and save them in the data processed folder

    Args:
        start (optional) : int      = first page
        end : (optional) int        = last page, 
        headers (optional) : dict   = headers for api request 

    Returns:
        None 
    """
    # check range
    if start < 0 or start > end:
        raise ValueError("start must be <=0 end start <= end")
    if end < 0:
        raise ValueError("end must be <= 0")
    if end > 99:
        end = 99

    # remove old files if any
    remove_raw_data()

    # get individual api responses and save them
    for page in range(start, end + 1):
        save_raw_joblist(page, headers=headers)

    # process raw data and delete raw files
    process_raw_data(delete_processed=True)

    # merge processed files and save them as a single json and csv file
    merge_processed_files(delete_source=True)

    # remove files if any
    remove_raw_data()


def update_all_source_data(end=0, start=0, headers={}):
    """
    Update source, download latest files and save them in the data processed folder
    Args:
        end : int                   = last page to update, set 0 for only one page
        start (optional) : int      = first page 
        headers (optional) : dict   = headers for api request 

    Returns:
        None 
    """
    get_all_source_data(start, end, headers)


if __name__ == "__main__":
    # job_list = get_raw_joblist(100, {})
    # print("Job list return length:", len(job_list[0]))
    # save_raw_joblist(0)
    # for i in range(0,99):
    #    save_raw_joblist(i)
    # process_raw_data(delete_processed=True)
    # merge_processed_files(delete_source=True)
    # remove_raw_data()
    update_all_source_data(200)