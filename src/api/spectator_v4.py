from .api_class import Api
import urllib

"""
Class that extends the api template, implements methods to access
champion mastery data from the champion_mastery_v4 riotgames api
"""
class Spectator_v4(Api):
    def __init__(self,region):
        super().__init__(region)
        self.endpoint_url = "spectator/v4/"

    """
    Gets active game information for encryptedSummonerId. If summoner is
    currently in a game, returns a CurrentGameInfo dictionary

    CurrentGameInfo dictionary contains gameId, type, duration, and players
    participating, along with MANY other fields listed in Riot games documentation.

    Sample CurrentGameInfo object: https://gist.github.com/mfro/f670ea56af1910a6afec
    """
    def get_active_game(self,encryptedSummonerID):
        url_summonerId = urllib.parse.quote(encryptedSummonerID)
        URL = self.base_url +self.endpoint_url+ "active-games/by-summoner/"+ url_summonerId + "?api_key=" + self.api_key

        return self.make_api_request(URL)
