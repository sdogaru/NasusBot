import sys
sys.path.append('../')

import unittest
from src.api.champion_v3 import champion_v3

class Test_champion_v3(unittest.TestCase):
    def test_get_free_champion_uds(self):
        cv3 = champion_v3()
        result = cv3.get_free_champion_ids()

        if result == -1:
            assert False, "Response code != 200"

        self.assertIsInstance(result,list)
        # riot gives between 10/15 free champs a week, so use >=
        self.assertTrue((len(result)>= 10))


if __name__ == '__main__':
    unittest.main()
