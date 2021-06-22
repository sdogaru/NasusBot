import sys
sys.path.append('../')

import unittest
from src.api.league_v4 import League_v4

class Test_summoner_v4(unittest.TestCase):
    def test_get_ranked_leagues(self):
        lv4 = League_v4("NA")
        result = lv4.get_ranked_leagues("Hc0X0_zh7f7Zu3jxNh4pvH8MVcneLsTcnNHUiHlOQwAXbWBj")

        self.assertTrue(result != -1 and len(result) == 0)

if __name__ == '__main__':
    unittest.main()
