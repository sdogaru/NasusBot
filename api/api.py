import requests
"""
   Template class for all the different api classes
   defines a request handler for api requests, and encapsulates
   API Key and base url for riot api
"""
class API:
    def __init__(self,api_key):
        self.api_key = api_key
        self.base_url = "https://na1.api.riotgames.com/lol/"

    """Riot API request handler to be used by all subclasses in their calls"""
    def make_request(url):
        try:
            response = requests.get(URL)
            if response.status_code != 200:
                raise Exception()

        #request fail case
        except Exception:
            print("Unsuccessful API Call: Status Code " + str(response.status_code))
            sys.exit(1)

        return response.json()
