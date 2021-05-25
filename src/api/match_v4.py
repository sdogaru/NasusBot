from .api_class import Api
import urllib

class match_v4(Api):
    def __init__(self):
        self.endpoint_url = "match/v4/"

    """
    Returns a MatchlistDto that contains up to 100 MatchReferenceDtos,
    which each contain data (gameid, role, champion,queue, time etc.)
    for a specific match played by the encryptedaccountId.

    MatchReferenceDtos, or matches played, can be filtered by parameters such as
    champion, queue, and time periods.

    Sample MatchListDto/MatchReferenceDTO: https://gist.github.com/mfro/f670ea56af1910a6afec
    """
    def get_match_list(self,encryptedaccountID,championId=None,queue=None,beginIndex=None,endIndex=None):
        url_accountId = urllib.parse.quote(encryptedaccountID)
        URL = self.base_url +self.endpoint_url+ "matchlists/by-account/"+ url_accountId  + "?"
        if championId != None:
            URL += "champion=" + str(championId) + "&"
        if queue != None:
            URL += "queue=" + str(queue) + "&"
        if beginIndex != None:
            URL += "beginIndex=" + str(beginIndex) + "&"
        if endIndex != None:
            URL += "endIndex=" + str(endIndex) + "&"

        URL += "api_key=" + self.api_key

        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result
