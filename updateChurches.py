import requests
from bs4 import BeautifulSoup
import re
import time


def getEntitiesWithoutLink(id):
    if id:
        url = f"https://eadventist.net/search/iframe?type=L&mask={id}"
        churches = getEntitiesFromLink(url + "&orgtype=5")
        companies = getEntitiesFromLink(url + "&orgtype=6")
        groups = getEntitiesFromLink(url + "&orgtype=15")
        
        return churches + companies + groups
    else:
        url = 'https://eadventist.net/en/search/iframe?mask=AN4F11&org=AN1111&orgtype=4&type=l'
        conferences = getEntitiesFromLink(url)
        return conferences

def getEntitiesFromLink(url, t=15):
    print(url)

    toReturn = []
    response = requests.get(url)
    if response.status_code != 200:
        if response.content.decode("utf-8") == "Retry later\n":
            time.sleep(t)
            return getEntitiesFromLink(url, t+15)
        else:
            print("failed")
            return {"error": "No file received from eAdventist"}
    soup = BeautifulSoup(response.content, 'html.parser')
    entities = soup.find_all(class_="my-2")
    for entity in entities:
        a_tag = entity.find('a')
        href = a_tag.get('href')
        eAdventistID = re.search(r'org=([A-Za-z0-9]+)', href)
        eAdventistID = eAdventistID.group(1)
        toReturn.append({'id': eAdventistID, 'name': a_tag.text})
        
    return toReturn

sOrgID = "AN1111"
#https://eadventist.net/en/search/iframe?mask=AN4F11&org=AN1111&orgtype=4&type=l
url = f"https://eadventist.net/search/iframe?type=L&mask={sOrgID}"


