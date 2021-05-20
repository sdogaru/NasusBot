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

        self.assertEqual(result,"oCwWLVEdQEKEEpo2NciVKqjjvRtgoGtFiw6L5OgMpe1q27Q")

    # invalid username case
    def test_bad_username_to_encryptedAccountID(self):
        sv4 = summoner_v4()
        result = sv4.username_to_encryptedAccountID(";;;;;;;;")
        self.assertEqual(result,-1)

    def test_username_to_level(self):
        sv4 = summoner_v4()
        result = sv4.username_to_level("Faze Seby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,2)

    def test_bad_username_to_level(self):
        sv4 = summoner_v4()
        result = sv4.username_to_level(";;;;;;;;")
        self.assertEqual(result,-1)

if __name__ == '__main__':
    unittest.main()
