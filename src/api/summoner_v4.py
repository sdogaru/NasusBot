from .api_class import Api
import urllib

"""
Class that extends the api template, implements methods to access user account
data like level, profile pic, and encryptedaccountID from the summoner_v4
riotgames api
"""
class Summoner_v4(Api):
    def __init__(self,region):
        super().__init__(region)
        self.endpoint_url = "summoner/v4/summoners/"

    """Given a players username, returns corresponding encryptedaccountID"""
    def username_to_encryptedAccountID(self,username):
        #convert string to url format and build url
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['accountId']

    """Given a players username, returns corresponding encryptedSummonerID"""
    def username_to_encryptedSummonerID(self,username):
        #convert string to url format and build url
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['id']


    """Given a players username, return usernames' account level"""
    def username_to_level(self,username):
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['summonerLevel']

    """Given a players username, return usernames' profileIconId
       Intented to be used in concert with datadragon to retrieve profile pics
    """
    def username_to_profileIconId(self,username):
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['profileIconId']

    """Given a players username, return profile puuid (for use with matchv5 api)
    """
    def username_to_puuid(self,username):
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['puuid']

    """Given a players username, returns correct spelling"""
    def username_to_username(self,username):
        #convert string to url format and build url
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['name']

    """Given a players username, returns correct spelling"""
    def encryptedAccountID_to_username(self,encryptedaccountID):
        #convert string to url format and build url
        url_username = urllib.parse.quote(encryptedaccountID)
        URL = self.base_url +self.endpoint_url+ "by-account/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['name']
