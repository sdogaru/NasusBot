import requests

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
CHAMPION_NAME_TO_ID = {v.lower(): k for k, v in CHAMPION_ID_TO_NAME.items()}
misspelled = [('aurelionsol','aurelion sol'),('jarvaniv','jarvan iv'),('leesin','lee sin'),('monkeyking','wukong'),('masteryi','master yi'),('missfortune','miss fortune'),('tahmkench','tahm kench'),('twistedfate','twisted fate'),('xinzhao','xin zhao'),('drmundo','dr mundo'),('drmundo','dr.mundo'),('drmundo','dr.mundo')]
for i in misspelled:
    CHAMPION_NAME_TO_ID[i[1]] = CHAMPION_NAME_TO_ID[i[0]]

#list of champion names
CHAMPION_LIST = list(CHAMPION_NAME_TO_ID.keys())


# Map id: map name dictionary
map_ids = requests.get("http://static.developer.riotgames.com/docs/lol/maps.json").json()
MAP_ID_TO_NAME = {i['mapId']:i['mapName'] for i in map_ids}

#queueId : queue name dictionary
queue_ids = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()
QUEUE_ID_TO_NAME = {i['queueId']:i['description'] for i in queue_ids}
QUEUE_NAME_TO_ID = {v:k for k,v in QUEUE_ID_TO_NAME.items()}

BLUE_TEAM_ID = 100
RED_TEAM_ID = 200

def get_champion_json(champion):
    # get tips from static datadragon that riot provides
    r = requests.get('http://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/champion/'+champion+'.json')
    if r.status_code != 200:
        print(r.status_code)
        return -1

    return r.json()
