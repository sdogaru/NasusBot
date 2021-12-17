from .api_class import Api
import urllib

class Match_v5(Api):
    def __init__(self,platform):
        super().__init__(platform=platform,region=True)
        self.endpoint_url = "match/v5/"

    """
    Returns a list of matchId strings. default length 20. Can specify start idx
    and a length between 0 and 100. Can specify queue as well.
    """
    def get_match_list(self,puuid,queue=None,start=None,count=None):
        url_puuid = urllib.parse.quote(puuid)
        URL = self.base_url +self.endpoint_url+ "matches/by-puuid/"+ url_puuid  + "/ids?"

        if queue != None:
            URL += "queue=" + str(queue) + "&"
        if start != None:
            URL += "start=" + str(start) + "&"
        if count != None:
            URL += "count=" + str(count) + "&"

        URL += "api_key=" + self.api_key

        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result


    """
    Returns data for a specified match (matchId) in a MatchDto
    MatchDto has hundreds of fields (in game stats, k/da, gold, items, ward score, participants...etc)
    that are specified at : https://developer.riotgames.com/apis#match-v4/GET_getMatch
    """
    def get_match(self,matchId):
        URL = self.base_url + self.endpoint_url + "matches/" + str(matchId) +"?api_key=" + self.api_key

        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['info']
