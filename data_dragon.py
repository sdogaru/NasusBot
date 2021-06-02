import requests

""" Onetime initialization of champion look up dictionaries/lists """
#access static data to create a dictionary of championIDs
version_no = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
champion_static_data = requests.get("http://ddragon.leagueoflegends.com/cdn/" +version_no+"/data/en_US/champion.json")
champion_data_dicts= champion_static_data.json().get('data')

#champion ID:Champion dictionary
CHAMPION_ID_TO_NAME = {}
for i in champion_data_dicts.keys():
    champ_key = champion_data_dicts.get(i).get('key')
    CHAMPION_ID_TO_NAME[int(champ_key)] = i

# Champion name:ID dictionary
CHAMPION_NAME_TO_ID = {v: k for k, v in CHAMPION_ID_TO_NAME.items()}

#list of champion names
CHAMPION_LIST = list(CHAMPION_NAME_TO_ID.keys())


"""http://ddragon.leagueoflegends.com/cdn/6.8.1/img/champion/Aatrox.png"""
