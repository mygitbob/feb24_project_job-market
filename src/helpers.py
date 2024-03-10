import requests
import os
from datetime import datetime
from constants import Constants, HTTPMethod
from logger import setup_logging, logging


headers = {"ACCEPT": "application/json"}

def api_test(url, connect_type=HTTPMethod.GET, headers=headers, request_body = {}): 

    logging.debug(f"{connect_type} REQUEST API FOR: {url}, HEADERS: {headers}, REQUEST_BODY: {request_body}")
    
    if connect_type == HTTPMethod.GET:
        response = requests.get(url, headers=headers)
    elif connect_type == HTTPMethod.POST:
        response = requests.post(url, headers=headers, data=request_body)
    else:
        raise Exception(f"Connection type not supported: {connect_type}")
    if response.status_code == 200:
        logging.debug(f"CONNECTION SUCCESSFUL, RESPONSE CODE: {response.status_code}")
        return response.text
    else:
        logging.error(f"CONNECTION NOT SUCCESSFUL, RESPONSE CODE: {response.status_code}")

def adzuna_api_joblist_test(page = 1): #page is int | list 
    result = []
    if isinstance(page, int):
        result = api_test(f"https://api.adzuna.com/v1/api/jobs/de/search/{page}?app_id={Constants.ADZUNA_APP_ID}&app_key={Constants.ADZUNA_API_KEY}",HTTPMethod.GET, headers)
    else:
        for i in page:
            response = api_test(f"https://api.adzuna.com/v1/api/jobs/de/search/{i}?app_id={Constants.ADZUNA_APP_ID}&app_key={Constants.ADZUNA_API_KEY}",HTTPMethod.GET, headers)
            if response:
                result.append(response)
            else:
                result.append(f'{{"__CLASS__":"{Constants.BAD_RESPONSE}"}}')
    return result

def muse_api_joblist_test(page): 
    result = []
    if isinstance(page, int):
        result = api_test(f"https://www.themuse.com/api/public/jobs?page={page}", HTTPMethod.GET, headers)
    else:
        for i in page:
            reponse = api_test(f"https://www.themuse.com/api/public/jobs?page={i}", HTTPMethod.GET, headers)
            if reponse:
                result.append(reponse)
            else:
                result.append(f'{{"__CLASS__":"{Constants.BAD_RESPONSE}"}}')
    return result

def jooble_api_joblist_test(data): 
    response = api_test(f"http://jooble.org/api/{Constants.JOOBLE_API_KEY}", HTTPMethod.POST, headers, data)
    if response:
        return response
    else:
        return f'{{"__CLASS__":{Constants.BAD_RESPONSE}}}'
    

def save_raw_data(fname, data):
    if isinstance(data, str):  
        with open(os.path.join(Constants.PATH_DATA_RAW, fname), 'w') as file:
            logging.debug(f"Write raw data: {fname}")
            file.write(data)
    elif isinstance(data, list):  
        with open(os.path.join(Constants.PATH_DATA_RAW, fname), 'w') as file:
            logging.debug(f"Write raw data: {fname}")
            file.write('[')            # multiple jsons have to be in an array
            for i, item in enumerate(data):
                file.write(item)
                if i < len(data) - 1:  # multiple jsons must be separated by ,
                    file.write(',')
                else:
                    file.write(']\n') 
    else:
        raise ValueError("Raw data to write must be string or list of strings")

def save_raw_api_joblist(api2contact, page=1, data={}):
    if api2contact not in Constants.API_JOBLIST:
        raise ValueError(f"api {api2contact} not in known list: {Constants.API_JOBLIST}]")
    now_str = str(datetime.now()).replace(" ","_")
    if api2contact == "adzuna":
        result = adzuna_api_joblist_test(page)
        if isinstance(page, int):
            fname = f"adzuna_raw_joblist.page{str(page)}.{now_str}.json"
        else:
            fname = f"adzuna_raw_joblist.multiple_pages_{page[0]}_{page[-1]}.{now_str}.json"
    elif api2contact == "muse":
        result = muse_api_joblist_test(page)
        if isinstance(page, int):
            fname = f"muse_raw_joblist.page{str(page)}.{now_str}.json"
        else:
            fname = f"muse_raw_joblist.multiple_pages_{page[0]}_{page[-1]}.{now_str}.json"
    elif api2contact == "jooble":
        result = jooble_api_joblist_test(data)
        fname = f"joodle_raw_joblist.{now_str}.json"
    save_raw_data(fname, result)
    

def okjob_test_api():
    start = 1
    end = 20
    response = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/1owGcfKZRHZq8wR7Iw6PVh6-ueR0weIVQMjxWW_0M6a8/values/Sheet1!A{start}:N{end}?key={Constants.OKJOB_API_KEY}")
    save_raw_data("okjob_raw.json", response.text)


def jobicy_test_api():
    response = requests.get(f"https://jobicy.com/api/v2/remote-jobs")
    save_raw_data("jobicy_raw.json", response.text)

if __name__ == "__main__" :
    
    setup_logging()
    #save_raw_api_joblist("jooble", data='{"keywords": "jav developer", "salary": "40000"}') 
    #save_raw_api_joblist("muse", page=range(2))
    #save_raw_api_joblist("adzuna", page=range(3))
    #okjob_test_api()
    jobicy_test_api()