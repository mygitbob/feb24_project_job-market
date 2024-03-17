import requests
from datetime import datetime
import re
from constants import Constants
from logger import setup_logging, logging
from helpers_io import save_raw_api_data, load_raw_api_data, save_proccessed_data



def get_raw_joblist(page, headers):
    """
    send api get request to load muse joblist
    """
    # TODO: register muse api key
    # url = f"https://www.themuse.com/api/public/jobs?api_key={Constants.MUSE_API_KEY}&page={page}"
    url = f"https://www.themuse.com/api/public/jobs?page={page}"
    print(url)

    logging.debug(f"GET REQUEST API FOR: {url}, HEADERS: {headers}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.debug(f"muse.py: {url}: CONNECTION SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    else:
        logging.error(f"muse.py: {url}: CONNECTION NOT SUCCESSFUL, RESPONSE CODE: {response.status_code}")
    return response.text, response.status_code


def save_raw_joblist(page=0, subdir = '', headers={}):
    """
     get muse raw joblist by api call and save it
    """
    response_data , response_code = get_raw_joblist(page, headers)
    if response_code == 200:
        if subdir == '':
            subdir = Constants.DIR_NAME_MUSE                    # create a folder for each source 
        now = datetime.now().replace(microsecond=0)
        fname = f"muse_raw_joblist.page{str(page)}.{now}.json"  # filename includes timestamp of request
        fname.replace(' ','_')                                  # no empty spaces in filename
        save_raw_api_data(fname, response_data, subdir)
    else:
        logging.debug(f"muse.py: get_and_save_raw_joblist: no data to save")
"""    
def proccess_raw_data(subdir=Constants.DIR_NAME_MUSE, fname='', delete_proccessed = False, write_json=True, write_csv=True):
    
    extract information from raw data

    data2process = load_raw_api_data(subdir=subdir, fname=fname)
    proccessed_files = []
    proccessed_data = []
    for d2p in data2process:
        fname, data = d2p
        if 'results' not in data:
            logging.error(f"muse.py: proccess_raw_data: no entry results for {fname}")
            break
        job_results = data['results']
        for job_result in job_results:
            job_entry = {}
            job_entry["job_title"] = job_result["name"]    
            job_entry["min_salary"], job_entry["max_salary"], job_entry['currency'] = extract_salary(job_result["contents"])
            job_entry["skills"] = extract_skills(job_result["contents"])
            job_entry["publication_date"] = job_result["publication_date"]
            job_entry["id"] = job_result["id"]
            job_entry["location"] = job_result["locations"]
            job_entry["job_categories"] = job_result["categories"]
            job_entry["experience"] = job_result["levels"][0]["short_name"]         # TODO:loop for multiple entries ?
            job_entry["html_link"] = job_result["refs"]["landing_page"] 
            job_entry["type"] = job_result["type"]                                  # not sure what this means
            job_entry["company_name"] = job_result["company"]["name"]
            job_entry["company_id"] = job_result["company"]["id"]                   # muse company id
            job_entry["source"] = "muse.com"                                        # name of data source
            job_entry["created"] = str(datetime.now().replace(microsecond=0))            # date when the script creates thsi entry
            proccessed_data.append(job_entry)    
        proccessed_files.append(fname)
        print(proccessed_data, proccessed_files)
    print(list((proccessed_data, proccessed_files)))
    input()
    save_proccessed_data(, Constants.DIR_NAME_MUSE, delete_files=delete_proccessed)
"""
def proccess_raw_data(subdir=Constants.DIR_NAME_MUSE, fname='', delete_proccessed = False, write_json=True, write_csv=True):
    """
    extract information from raw data
    """
    data2process = load_raw_api_data(subdir=subdir, fname=fname)
    for d2p in data2process:
        fname, data = d2p
        all_entries = []
        if 'results' not in data:
            logging.error(f"muse.py: proccess_raw_data: no entry results for {fname}")
            break
        job_results = data['results']
        for job_result in job_results:
            job_entry = {}
            job_entry["job_title"] = job_result["name"]    
            job_entry["min_salary"], job_entry["max_salary"], job_entry['currency'] = extract_salary(job_result["contents"])
            job_entry["skills"] = extract_skills(job_result["contents"])
            job_entry["publication_date"] = job_result["publication_date"]
            job_entry["id"] = job_result["id"]
            job_entry["location"] = job_result["locations"]
            job_entry["job_categories"] = job_result["categories"]
            job_entry["experience"] = job_result["levels"][0]["short_name"]         # TODO:loop for multiple entries ?
            job_entry["html_link"] = job_result["refs"]["landing_page"] 
            job_entry["type"] = job_result["type"]                                  # not sure what this means
            job_entry["company_name"] = job_result["company"]["name"]
            job_entry["company_id"] = job_result["company"]["id"]                   # muse company id
            job_entry["source"] = "muse.com"                                        # name of data source
            job_entry["created"] = str(datetime.now().replace(microsecond=0))            # date when the script creates thsi entry
            all_entries.append(job_entry)    
        save_proccessed_data(all_entries, fname, Constants.DIR_NAME_MUSE, delete_source=delete_proccessed, write_json=write_json, Write_csv=write_csv)

def extract_salary(html_text):
    """
    """
    pattern = rf'<br>The typical pay range for this role is:<br><br>(.*?)<br>'
    matches = re.search(pattern, html_text)

    if matches:
        currency = matches.group(1).strip()[0]
        if currency not in Constants.KOWN_CURRENCY:
            currency = "UNKOWN"
        min_nr = matches.group(1).split('-')[0].strip()[1:]
        max_nr = matches.group(1).split('-')[1].strip()[1:]
    else: 
        min_nr = max_nr = currency = "NOT_FOUND"
    return min_nr, max_nr, currency

def extract_skills(html_text):
    return "to_be_implemented"

if __name__ == "__main__":
    #job_list = get_raw_joblist(0, {})
    #print("Job list return length:", len(job_list[0]))
    #for i in range(5):
    #    save_raw_joblist(i)
    #save_raw_joblist(0)
    proccess_raw_data(delete_proccessed=False)