import sys
sys.path.append('../')

import unittest
from src.api.summoner_v4 import summoner_v4

class Test_summoner_v4(unittest.TestCase):
    # username exists, correct functionality case
    def test_username_to_encryptedAccountID(self):
        sv4 = summoner_v4()
        result = sv4.username_to_encryptedAccountID("Šeby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,"JLzDAXZ89AGuYb1Std1IF_PJ5wqs1WORI4URcV6fbq7mEQY")

    # invalid username case
    def test_bad_username_to_encryptedAccountID(self):
        sv4 = summoner_v4()
        result = sv4.username_to_encryptedAccountID(";;;;;;;;")
        self.assertEqual(result,-1)
        
if __name__ == '__main__':
    unittest.main()
