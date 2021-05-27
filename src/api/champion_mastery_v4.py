from .api_class import Api
import urllib

"""
Class that extends the api template, implements methods to access
champion mastery data from the champion_mastery_v4 riotgames api
"""
class Champion_mastery_v4(Api):
    def __init__(self):
        self.endpoint_url = "champion-mastery/v4/"


    """
    Returns array of ChampionMasteryDto dictionaries containing champion mastery data,
    for each of the encryptedSummonerID's champions.

    Sample Return Value (ChampionMasteryDto):
    [{
    "championId": 99,
    "championLevel": 7,
    "championPoints": 130744,
    "lastPlayTime": 1619503193000,
    "championPointsSinceLastLevel": 109144,
    "championPointsUntilNextLevel": 0,
    "chestGranted": false,
    "tokensEarned": 0,
    "summonerId": "JLzDAXZ89AGuYb1Std1IF_PJ5wqs1WORI4URcV6fbq7mEQY"
    }, ...]
    """
    def get_full_championHistory(self,encryptedSummonerID):
        url_summonerId = urllib.parse.quote(encryptedSummonerID)
        URL = self.base_url +self.endpoint_url+ "champion-masteries/by-summoner/"+ url_summonerId + "?api_key=" + self.api_key

        return self.make_api_request(URL)

    """
    Returns dictionary containing summoner's champion mastery data for specified
    championId

    Sample Return Value (ChampionMasteryDto):
    {
    "championId": 99,
    "championLevel": 7,
    "championPoints": 130744,
    "lastPlayTime": 1619503193000,
    "championPointsSinceLastLevel": 109144,
    "championPointsUntilNextLevel": 0,
    "chestGranted": false,
    "tokensEarned": 0,
    "summonerId": "JLzDAXZ89AGuYb1Std1IF_PJ5wqs1WORI4URcV6fbq7mEQY"
    }
    """
    def get_individual_championHistory(self,encryptedSummonerID,championId):
        url_summonerId = urllib.parse.quote(encryptedSummonerID)
        URL = self.base_url +self.endpoint_url+ "champion-masteries/by-summoner/"+ url_summonerId +"/by-champion/"+str(championId) +"?api_key=" + self.api_key

        return self.make_api_request(URL)

    """
    Returns integer of summoner's total mastery score, summed across all champions
    """
    def get_total_mastery_score(self,encryptedSummonerID):
        url_summonerId = urllib.parse.quote(encryptedSummonerID)
        URL = self.base_url +self.endpoint_url+ "scores/by-summoner/"+ url_summonerId +"?api_key=" + self.api_key

        return self.make_api_request(URL)
