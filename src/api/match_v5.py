from .api_class import Api
import urllib

class Match_v5(Api):
    def __init__(self,region):
        super().__init__(platform=None,region=region)
        self.endpoint_url = "match/v5/"


m = Match_v5('AMERICAS')
print(m)
