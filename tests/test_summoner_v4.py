import sys
sys.path.append('../')

import unittest
from src.api.summoner_v4 import Summoner_v4

class Test_summoner_v4(unittest.TestCase):
    # username exists, correct functionality case
    def test_username_to_encryptedAccountID(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_encryptedAccountID("Šeby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,"oCwWLVEdQEKEEpo2NciVKqjjvRtgoGtFiw6L5OgMpe1q27Q")

    # invalid username case
    def test_bad_username_to_encryptedAccountID(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_encryptedAccountID(";;;;;;;;")
        self.assertEqual(result,-1)

    def test_username_to_encryptedSummonerID(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_encryptedSummonerID("Šeby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,"JLzDAXZ89AGuYb1Std1IF_PJ5wqs1WORI4URcV6fbq7mEQY")

    # invalid username case
    def test_bad_username_to_encryptedSummonerID(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_encryptedSummonerID(";;;;;;;;")
        self.assertEqual(result,-1)

    # access account level for an account i dont use anymore
    def test_username_to_level(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_level("Faze Seby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,2)

    # invalid username case
    def test_bad_username_to_level(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_level(";;;;;;;;")
        self.assertEqual(result,-1)

    def test_username_to_profileIconId(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_profileIconId("Šeby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,20)

    # invalid username case
    def test_bad_username_to_profileIconId(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_profileIconId(";;;;;;;;")
        self.assertEqual(result,-1)


    def test_username_to_puuid(self):
        sv4 = Summoner_v4("NA")
        result = sv4.username_to_puuid("Šeby")
        if result == -1:
            assert False, "Response code != 200"

        self.assertEqual(result,"e3eRV-PsBh0hTqsW5cedfsR1qyJpXKaoGwqD_uM9jAlov2z9s8JZFUSbCRkDaYmLucARCzIicIB0gA")

if __name__ == '__main__':
    unittest.main()
