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

        self.assertEqual(result,"pYRKtrHI8ZH7627I-BUjzrGBRoKPC2XekyqL1U_qK5G7Fzk")

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

        self.assertEqual(result,"plTojZbQDi0rL3fwj0SI8cvdcYLX9sQA-1ZvaKF6gpBguMc")

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

        self.assertEqual(result,"lTCVM2bkGEF7oKLudGVq-pkOmmMNirbUpC1Rbsoh04I95QW0d9LuHYTxRQz_obPDc22lcGnDHcR3qw")

if __name__ == '__main__':
    unittest.main()
