class summoner_v4(API):
    def __init__(self):
        self.endpoint_url = "champion-mastery/v4/"

    """Given a players username, returns corresponding encryptedaccountID"""
    def username_to_encryptedAccountID(username):
        #convert string to url format and build url
        url_username = username.replace(" ","%20")
        URL = self.base_url + "summoners/by-name/"+ url_username + "?api_key=" + self.api_key

        #GET request to api endpoint
        return self.make_request(URL)['id']
