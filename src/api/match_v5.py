from .api_class import Api
import urllib

class Match_v5(Api):
    def __init__(self,region):
        super().__init__(platform=None,region=region)
        self.endpoint_url = "match/v5/"


    def get_match_list(self,puuid,queue=None,start=None,count=None):
        url_puuid = urllib.parse.quote(encryptedaccountID)
        URL = self.base_url +self.endpoint_url+ "matchlists/by-puuid/"+ url_accountId  + "?"

        if queue != None:
            URL += "queue=" + str(queue) + "&"
        if start != None:
            URL += "start=" + str(beginIndex) + "&"
        if count != None:
            URL += "count=" + str(endIndex) + "&"

        URL += "api_key=" + self.api_key

        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result
