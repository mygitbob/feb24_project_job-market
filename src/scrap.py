"""
import os
import re
from bs4 import BeautifulSoup as bs
import requests
from urllib.parse import urlparse
from constants import Constants
from logger import setup_logging, logging

def reduce_newlines(text):
    lines = text.split('\n')
    filtered_lines = [lines[0]]  
    for line in lines[1:]:
        if line.strip():  
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def get_html_source(url, **parmas):

    required_keys = set(re.findall(r'\{([^{}]+)\}', url))
    provided_keys = set(parmas.keys())
    missing_keys = required_keys - provided_keys
    if missing_keys:
        raise ValueError(f"Missing required keyword arguments: {missing_keys}")
    url = url.format(**parmas)
    response= requests.get(url)
    if response.status_code != 200:
        #logging.error(f"CONNECTION NOT SUCCESSFUL, URL:{url} , RESPONSE CODE: {response.status_code}")
        return
    else:
        #logging.debug(f"CONNECTION SUCCESSFUL, URL:{url}, RESPONSE CODE: {response.status_code}")
        save_html_source(url, response.text)
    

def save_html_source(url, data):
    base_url = urlparse(url).netloc
    query = urlparse(url).query
    dir2save = os.path.join(Constants.PATH_DATA_RAW, base_url)
    if not os.path.isdir(dir2save):
        os.mkdir(dir2save)
    file2save = os.path.join(dir2save, query + ".html")
    with open(file2save, "w") as f:
        f.write(data)

def get_joblist_entires_welcome2tj(file):
    filepath = os.path.join(Constants.PATH_DATA_RAW, "www.welcometothejungle.com", file)
    with open(filepath, "r") as f:
        source = f.read()
    
    soup = bs(source, "lxml")

    res = []
    list_tags2search = "li.sc-bXCLTC.kkKAOM.ais-Hits-list-item" #sc-1wqurwm-0 cCiCwl ais-Hits-list

    list_items = soup.select(list_tags2search)
    print("list items:", list_items)
    for item in list_items:
        print('item:', item)
        div_element = item.select_one('div.base-card')
        if div_element:
            text = div_element.get_text().strip()
            print('text:', text)
            res.append(reduce_newlines(text))
    return res 

def welcome_jungle(country_code, query):
    url = "https://www.welcometothejungle.com/en/jobs?refinementList%5Boffices.country_code%5D%5B%5D={country_code}&query={query}&page=1"
    page = requests.get(url)
    print("www.welcometothejungle.com")
    print("HTTP Status Code:", page.status_code)
    soup = bs(page.content, "lxml")

    res = []
    list_tags2search = "li.sc-bXCLTC.kkKAOM.ais-Hits-list-item"

    list_items = soup.select(list_tags2search)
    for item in list_items:
        div_element = item.select_one('div.base-card')
        if div_element:
            text = div_element.get_text().strip()
            res.append(reduce_newlines(text))
    return res

def linkedin(keywords, location):
    url = f"https://de.linkedin.com/jobs/search?keywords={keywords}&location={location}&trk=guest_homepage-basic_jobs-search-bar_search-submit&position=1&pageNum=0"
    

    page = requests.get(url)
    print("de.linkedin.com")
    print("HTTP Status Code:", page.status_code)
    soup = bs(page.content, "lxml")

    res = []
    list_tags2search = 'ul.jobs-search__results-list li'

    list_items = soup.select(list_tags2search)
    for item in list_items:
        div_element = item.select_one('div.base-card')
        if div_element:
            text= div_element.get_text().strip()
            res.append(reduce_newlines(text))
    return res

if __name__ == "__main__":

    setup_logging()
    url2test = "https://uk.indeed.com/jobs?q=Data+Engineer&l=London&from=searchOnHP&vjk=86f53586b1361ea9"
    url2test = "https://www.adzuna.de/details/4551219643?utm_medium=api&utm_source=fb3d1b6c"
    url2test = "https://www.glassdoor.de/Gehalt/idealo-internet-Data-Engineer-Geh%C3%A4lter-E947456_D_KO16,29.htm"
    url2test = "https://www.linkedin.com/jobs/search/?currentJobId=3830628620&f_SB2=41&geoId=101165590&location=Vereinigtes%20K%C3%B6nigreich&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
    url2test = "https://de.indeed.com/?advn=8594954787924193&vjk=74b51e4e8c38f3bf"
    url2test = "https://www.indeed.com/jobs?as_and=data+scientist&as_phr=&as_any=&as_not=&as_ttl=&as_cmp=&jt=all&st=&salary=&radius=25&l=boston&fromage=any&limit=100&start=0&sort=&psf=advsrch"
    url2test = "https://www.welcometothejungle.com/en/jobs?refinementList%5Boffices.country_code%5D%5B%5D=US&query=it&page=1"
    url2test = "https://www.welcometothejungle.com/en/companies/carrefour/jobs/directeur-de-magasin-ecole-itinerant-f-h_massy?q=32f73f67eed3a8845726fead19353ed3&o=96d58415-bb96-44aa-a797-c44892171924"
    url2test = "https://www.themuse.com/jobs/cvshealth/pharmacy-technician-3aa6cd"
    url2test = "https://jooble.org/jdp/-4295285951228261990"
    url2test = get_html_source(url2test)
    

    #url2test = "https://www.welcometothejungle.com/en/jobs?refinementList%5Boffices.country_code%5D%5B%5D={country_code}&query={query}&page={page}"
    #get_html_source(url2test, country_code="de", query="it", page="1")
    #u2t = "https://www.glassdoor.com/Job/united-kingdom-data-engineer-jobs-SRCH_IL.0,14_IN2_KO15,28.htm"
    #get_html_source(u2t)
    #file = os.listdir(os.path.join(Constants.PATH_DATA_RAW, "www.welcometothejungle.com"))[0]
    #print(get_joblist_entires_welcome2tj(file))

    res_wj = welcome_jungle(country_code="de", query="it")
    res_li = linkedin(keywords="it", location="Berlin")
    print("Welcome to the Jungle Results")
    print(res_wj)
    print("-" * 100)
    print("LinkedIn Results")
    print(res_li)
    print("-" * 100)
    """