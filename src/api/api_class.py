import requests
import os
from dotenv import load_dotenv
import sys

load_dotenv()
API_KEY = os.getenv('API_KEY')
"""
   Template class for all the different api classes
   defines a request handler for api requests, and encapsulates
   API Key and base url for riot api
"""
class Api:
    api_key = API_KEY
    base_url = "https://na1.api.riotgames.com/lol/"

    """Riot API request handler to be used by all subclasses in their calls"""
    def make_request(self,url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception()

        #request fail case
        except Exception:
            print("Unsuccessful API Call: Status Code " + str(response.status_code))
            sys.exit(1)

        return response.json()


    def rate_limit_check():
        return None
