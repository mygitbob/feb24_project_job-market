from bs4 import BeautifulSoup as bs
import requests

def reduce_newlines(text):
    lines = text.split('\n')
    filtered_lines = [lines[0]]  
    for line in lines[1:]:
        if line.strip():  
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def welcome_jungle(country_code, query):
    url = "https://www.welcometothejungle.com/en/jobs?refinementList%5Boffices.country_code%5D%5B%5D={country_code}}&query={query}}&page=1"
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
    res_wj = welcome_jungle(country_code="de", query="it")
    res_li = linkedin(keywords="it", location="Berlin")
    print("Welcome to the Jungle Results")
    print(res_wj)
    print("-" * 100)
    print("LinkedIn Results")
    print(res_li)
    print("-" * 100)