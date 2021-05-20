import sys
sys.path.append('../')

import unittest
from src.api.summoner_v4 import summoner_v4

summoner_v4 = summoner_v4()
result = summoner_v4.username_to_encryptedAccountID("Šeby")
print(result)
