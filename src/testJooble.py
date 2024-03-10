import http.client
from constants import Constants
import requests

def test_httpclient():
    
    host = 'jooble.org'
    key = Constants.JOOBLE_API_KEY

    connection = http.client.HTTPConnection(host)
    #request headers
    headers = {"Content-type": "application/json"}
    #body = '{ "keywords": "it", "location": "Bern"}'

    #connection.request('POST','/api/' + key, body, headers)
    connection.request("GET", "/partner/ppc",  allow_redirects=True)
    response = connection.getresponse()
    print(response.status, response.reason)
    print(response.read().decode())

    connection.close()

def test_request():

    #url = "https://jooble.org/away/-4369338781514842088?p=1&pos=5&pageType=21&ckey=NONE&sid=4430753394762102870&jobAge=104&relb=115&brelb=115&scr=19096.516432149314&bscr=19096.516432149314&elckey=1307162172655746199&searchTestGroup=1_1116_2&iid=3726824327787282667"
    #url = "https://jooble.org"
    url = "https://jooble.org/jdp/5710057045122090913?p=1&pos=5&pageType=21&ckey=NONE&sid=4430753394762102870&jobAge=104&relb=115&brelb=115&scr=19096.516432149314&bscr=19096.516432149314&elckey=1307162172655746199&searchTestGroup=1_1116_2&iid=3726824327787282667"
    # Anfrage senden und Weiterleitungen erlauben
    response = requests.get(url)

    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        print("Anfrage erfolgreich!")
        print(response.text)
    else:
        print("Fehler:", response.status_code)

test_request()