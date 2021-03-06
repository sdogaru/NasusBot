import sys
sys.path.append('../')

import unittest
from src.api.champion_mastery_v4 import Champion_mastery_v4

class Test_champion_mastery_v4(unittest.TestCase):
    def test_get_full_championHistory(self):
        cmv4 = Champion_mastery_v4("NA")
        result = cmv4.get_all_champion_mastery("plTojZbQDi0rL3fwj0SI8cvdcYLX9sQA-1ZvaKF6gpBguMc")
        if result == -1:
            assert False, "Response code != 200"

        # non empty champion values
        self.assertTrue(len(result) > 0 and result[0]['championId'] != None)


    def test_get_individual_championHistory(self):
        cmv4 = Champion_mastery_v4("NA")

        #look up lux mastery on my personal acc
        result = cmv4.get_individual_champion_mastery("plTojZbQDi0rL3fwj0SI8cvdcYLX9sQA-1ZvaKF6gpBguMc",99)
        if result == -1:
            assert False, "Response code != 200"

        # my Lux is level 7 with > 130k points
        self.assertTrue(result['championPoints'] > 130000 and result['championLevel'] == 7 )


    def test_get_total_mastery_score(self):
        cmv4 = Champion_mastery_v4("NA")
        # test for my personal acc total mastery
        result = cmv4.get_total_mastery_score("plTojZbQDi0rL3fwj0SI8cvdcYLX9sQA-1ZvaKF6gpBguMc")
        if result == -1:
            assert False, "Response code != 200"
        # my personal acc total mastery is >= 190
        self.assertTrue(result >= 190)

if __name__ == '__main__':
    unittest.main()
