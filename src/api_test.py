import os
import requests
from urllib.parse import urlparse

# https://developer.adzuna.com/overview
ADZUNA_APP_ID = "fb3d1b6c"
ADZUNA_APP_KEY = "d1999430f1b272b9af611b798e8b0789"

page_number = 1

header_list = [{
    "ACCEPT": "application/json",  
}]
url_list = [f"https://api.adzuna.com/v1/api/jobs/de/search/{page_number}?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}",
            f"https://www.themuse.com/api/public/jobs?page={page_number}"]

urls = zip(url_list, header_list *len(url_list) )

for url, headers in urls:

    print("REQUEST API FOR:",url, headers)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.text  
        fname =  urlparse(url).hostname + f"--page{page_number}.json"
        path_src = os.path.join(os.path.dirname(__file__))
        path_project = path_src.split("src")[0] 
        path_data = path_project + "data/raw/"
        print(path_data)
        with open(f"{path_data}{fname}", 'w') as file:
            file.write(data)
    else:
        print('ERROR:', response.status_code)
    
