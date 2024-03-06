import os
import requests
from urllib.parse import urlparse

# https://developer.adzuna.com/overview
ADZUNA_APP_ID = "fb3d1b6c"
ADZUNA_APP_KEY = "d1999430f1b272b9af611b798e8b0789"

JOOBLE_API_KEY = "b056f9bf-136f-4fd5-8721-6fdc0d4453bc"

page_number = 1

header = {"ACCEPT": "application/json"}

urls = [(f"https://api.adzuna.com/v1/api/jobs/de/search/{page_number}?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}","GET", header, None),
            (f"https://www.themuse.com/api/public/jobs?page={page_number}", "GET", header, None),
            (f"http://jooble.org/api/{JOOBLE_API_KEY}", "POST", header, '{ "keywords": "it", "location": "Berlin"}')]


print(list(urls))
for url, connect_type, headers, body in urls:

    print("REQUEST API FOR:",url,connect_type, headers)
    if connect_type == "GET":
        response = requests.get(url, headers=headers)
        fname =  urlparse(url).hostname + f"--page{page_number}.json"
    else:
        response = requests.post(url, headers=headers, data=body)
        fname =  urlparse(url).hostname + f"--data:{body}.json"
    if response.status_code == 200:
        data = response.text  
        path_src = os.path.join(os.path.dirname(__file__))
        path_project = path_src.split("src")[0] 
        path_data = path_project + "data/raw/"
        with open(f"{path_data}{fname}", 'w') as file:
            file.write(data)
    else:
        print('ERROR:', response.status_code)
    
