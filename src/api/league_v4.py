from .api_class import Api
import urllib

class League_v4(Api):
    def __init__(self,region):
        super().__init__(region)
        self.endpoint_url = "league/v4/"

    """
    Returns a Set of LeagueEntryDTOs- each of which contains the summoners
    rank, win/loss count, and more data for a particular ranked league (solo/duo,flex,etc.)
    """
    def get_ranked_leagues(self,encryptedSummonerID):
        url_summonerId = urllib.parse.quote(encryptedSummonerID)
        URL = self.base_url +self.endpoint_url+ "entries/by-summoner/"+url_summonerId +"?api_key=" + self.api_key

        #GET request to api endpoint
        return self.make_api_request(URL)
