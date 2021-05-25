from .api_class import Api
import urllib

"""
Class that extends the api template, implements methods to access free
champion data from the champion_v3 riotgames api
"""
class Champion_v3(Api):
    def __init__(self):
        self.endpoint_url = "platform/v3/champion-rotations"


    """
    Returns a list of the current free champion ids
    ids intended to be used with the datadragon

    Sample Return: [99,33,...]
    """
    def get_free_champion_ids(self):
        URL = self.base_url +self.endpoint_url+ "?api_key=" + self.api_key

        #GET request to api endpoint
        result = self.make_api_request(URL)
        if result == -1:
            return -1
        else:
            return result['freeChampionIds']
