import sys
sys.path.append('../')

import unittest
from src.api.match_v5 import Match_v5

class Test_match_v5(unittest.TestCase):
    def test_match_v5_ctor(self):
        mv5 = Match_v5("AMERICAS")
        self.assertTrue(mv5.base_url == "https://americas.api.riotgames.com/lol/")

        

if __name__ == '__main__':
    unittest.main()
