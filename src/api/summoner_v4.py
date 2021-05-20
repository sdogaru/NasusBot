from .api_class import Api
import urllib

class summoner_v4(Api):
    def __init__(self):
        super().__init__()
        self.endpoint_url = "summoner/v4/summoners/"

    """Given a players username, returns corresponding encryptedaccountID"""
    def username_to_encryptedAccountID(self,username):
        #convert string to url format and build url
        url_username = urllib.parse.quote(username)
        URL = self.base_url +self.endpoint_url+ "by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        return self.make_request(URL)['id']
