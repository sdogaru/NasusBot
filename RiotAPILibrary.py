import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

def username_to_encryptedID(username):
    #convert string to url format and build url
    url_username = username.replace(" ","%20")
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+ url_username + "?api_key=" + API_KEY

    #GET request to api endpoint
    try:
        response = requests.get(URL)
        if response.status_code != 200:
            raise Exception()

    #request fail case
    except Exception:
        print("Unsuccessful API Call: Status Code " + str(accountData.status_code))
        sys.exit(1)

    return response.json()['id']

print(username_to_encryptedID("Šeby"))
