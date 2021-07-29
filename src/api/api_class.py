import requests
import os
from dotenv import load_dotenv
import sys
import time

# use .env file to load secret api key
load_dotenv()
API_KEY = os.environ['API_KEY']

PLATFORM_ROUTING = {"BR":	"br1.api.riotgames.com",
    "EUNE":	"eun1.api.riotgames.com",
    "EUW":	"euw1.api.riotgames.com",
    "JP":"jp1.api.riotgames.com",
    "KR":"kr.api.riotgames.com",
    "LAN":"la1.api.riotgames.com",
    "LAS":"la2.api.riotgames.com",
    "NA":"na1.api.riotgames.com",
    "OCE":"oc1.api.riotgames.com",
    "TR":"tr1.api.riotgames.com",
    "RU":"ru.api.riotgames.com"}

REGION_ROUTING = {"AMERICAS":"americas.api.riotgames.com",
"ASIA":	"asia.api.riotgames.com",
"EUROPE":"europe.api.riotgames.com"}


"""
   Template class for all the different api classes
   defines a request handler for api requests, and encapsulates
   API Key and base url for riot api
"""
class Api():
    def __init__(self,region):
        self.api_key = API_KEY
        self.base_url = "https://"+PLATFORM_ROUTING[region]+"/lol/"

    """Riot API request handler to be used by all subclasses in their calls"""
    def make_api_request(self,url):
        try:
            # rate limit edge case
            response = requests.get(url)

            # if 504, try again
            if response.status_code == 504 or response.status_code == 503:
                print("504/503, trying again here.")
                response = requests.get(url)

            if response.status_code == 429:
                print("RATE LIMIT 429 error")
                print("sleeping")
                time.sleep(120)
                print("awake now")
                response = requests.get(url)

            if response.status_code != 200:
                print("RIOT API RETURNED STATUS CODE: " + str(response.status_code))
                raise Exception()

        #request fail case
        except Exception:
            return -1

        return response.json()


    def rate_limit_check():
        return None
