import sys
sys.path.append('../')

import unittest
from src.api.match_v5 import Match_v5

class Test_match_v5(unittest.TestCase):
    def test_match_v5_ctor(self):
        mv5 = Match_v5("NA")
        self.assertTrue(mv5.base_url == "https://americas.api.riotgames.com/lol/")


    def test_get_match_list(self):
        mv5 = Match_v5("NA")
        result = mv5.get_match_list("pPMVtELOe6WzNPTMpKkwnfSSQCrP_qJF5zr95cVg64lDxfeAs2Lc17KmG2vy2vLRwQ63g_q4hK4xrQ")

        if result == -1:
            assert False, "Response code != 200"

        self.assertTrue(len(result) == 20)

    def test_get_match(self):
        mv5 = Match_v5("NA")
        result = mv5.get_match('NA1_4137828491')

        if result == -1:
            assert False, "Response code != 200"

        self.assertTrue(
            result['gameDuration'] == 1729 and
            result['gameMode'] == 'ULTBOOK' and
            result['gameCreation'] == 1639378901000
        )

if __name__ == '__main__':
    unittest.main()
