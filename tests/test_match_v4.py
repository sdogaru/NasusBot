import sys
sys.path.append('../')

import unittest
from src.api.match_v4 import Match_v4

class Test_match_v4(unittest.TestCase):
    # test that call to get_match_list returns 100 matchReferenceDtos
    def test_get_match_list(self):
        mv4 = Match_v4()
        result = mv4.get_match_list("oCwWLVEdQEKEEpo2NciVKqjjvRtgoGtFiw6L5OgMpe1q27Q")

        if result == -1:
            assert False, "Response code != 200"


        self.assertTrue(len(result['matches']) == 100)

    # test call to get_match_list with begin and end index specified
    def test_get_match_list_bounded(self):
        mv4 = Match_v4()
        result = mv4.get_match_list("oCwWLVEdQEKEEpo2NciVKqjjvRtgoGtFiw6L5OgMpe1q27Q",beginIndex=100,endIndex=150)

        if result == -1:
            assert False, "Response code != 200"

        self.assertTrue(len(result['matches']) == 50)

    # test call to get_match_list with specified champion (RIVEN)
    def test_get_match_list_champion(self):
        mv4 = Match_v4()
        result = mv4.get_match_list("oCwWLVEdQEKEEpo2NciVKqjjvRtgoGtFiw6L5OgMpe1q27Q",championId=92)

        if result == -1:
            assert False, "Response code != 200"

        self.assertTrue(len(result['matches']) == 2)

    def test_get_match(self):
        mv4 = Match_v4()
        result = mv4.get_match(3918284283)

        if result == -1:
            assert False, "Response code != 200"


        self.assertTrue(
            result['gameDuration'] == 1240 and
            result['gameMode'] == 'CLASSIC' and
            result['gameCreation']== 1621837483489
        )


if __name__ == '__main__':
    unittest.main()
