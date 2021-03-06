import discord
import os
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

from src.api.summoner_v4 import Summoner_v4
from src.api.league_v4 import League_v4
from src.api.champion_v3 import Champion_v3
from src.api.spectator_v4 import Spectator_v4
from src.api.match_v5 import Match_v5
from src.api.champion_mastery_v4 import Champion_mastery_v4

from data_dragon import CHAMPION_ID_TO_NAME
from data_dragon import CHAMPION_NAME_TO_ID
from data_dragon import QUEUE_ID_TO_NAME
from data_dragon import QUEUE_NAME_TO_ID
from data_dragon import MAP_ID_TO_NAME
from data_dragon import BLUE_TEAM_ID,RED_TEAM_ID
from data_dragon import get_champion_json
from data_dragon import DD_BASE_URL


import datetime
import pandas as pd
import numpy
import time
import requests

#.env os variables
load_dotenv()

# MongoDB Atlas
import pymongo
client = pymongo.MongoClient(os.environ['DB_PREFIX']+os.environ['DB_TOKEN']+os.environ['DB_SUFFIX'])
db = client.NasusBot

# Discord.py / slash commands
intents = discord.Intents(messages=True, guilds=True)
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.
enabled = True
EMBED_COLOR = 0x9932CC

"""
When the bot is added to a server, send a gif in chat to introduce
"""
@client.event
async def on_guild_join(guild):
    #general = discord.utils.find(lambda x: x.name == 'general',  guild.text_channels)
    if len(guild.text_channels) > 1: #general:
        embed = discord.Embed(color=EMBED_COLOR,title="Hi, I'm NasusBot - a Discord bot for all things League of Legends! To get started, type /")
        embed.set_image(url="https://64.media.tumblr.com/0e48c6d56405dc1228bcfc8879c51046/f75a4d609d3d34a7-52/s400x600/8901bb6912e817dfdd022e989ff5b2f0a634dca3.gif")
        await guild.text_channels[0].send(embed=embed)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global enabled

    if message.author == client.user:
        return


"""
/rank [username]
- returns rank, lp, and winrate for username
"""
@slash.slash(name="rank",
             description="View a summoner's soloq rank, lp, and ranked winrate.",
             options=[
                create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                   create_choice(
                     name="NA",
                     value="NA"
                   ),
                   create_choice(
                     name="EUW",
                     value="EUW"
                   ),
                   create_choice(
                     name="EUNE",
                     value="EUNE"
                   ),
                   create_choice(
                     name="KR",
                     value="KR"
                   ),
                   create_choice(
                     name="OCE",
                     value="OCE"
                   ),
                   create_choice(
                     name="TR",
                     value="TR"
                   ),
                   create_choice(
                     name="JP",
                     value="JP"
                   ),
                   create_choice(
                     name="LAN",
                     value="LAN"
                   ),
                   create_choice(
                     name="LAS",
                     value="LAS"
                   ),
                   create_choice(
                     name="RU",
                     value="RU"
                   ),
                 ]),
                create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )
             ])
async def rank(ctx,username: str,region: str):
    sv4 = Summoner_v4(region)
    lv4 = League_v4(region)

    embed = discord.Embed(color=EMBED_COLOR,title="Fetching ranked data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username+" could not be found on "+region+".")
        await message.edit(content="",embed=error_embed)
        return
    else:
        # display loading gif while data is retrieved

        username = sv4.username_to_username(username)
        # check for successful request for league entries
        leagueEntryDTOs = lv4.get_ranked_leagues(encryptedSummonerID)
        if leagueEntryDTOs == -1:
            error_embed = discord.Embed(color=EMBED_COLOR,title=f"Error accessing Riot Games API. Please try again later.")
            await message.edit(content="",embed=error_embed)
            return

        # filter on soloqueue
        leagueEntryDTOs = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_SOLO_5x5"]
        if len(leagueEntryDTOs) == 0:
            error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username+" is not ranked in soloqueue for the current season.")
            await message.edit(content="",embed=error_embed)
            return
        else:
            # get data from dto and format into discord message
            tier = leagueEntryDTOs[0]['tier']
            rank = leagueEntryDTOs[0]['rank']
            lp = str(leagueEntryDTOs[0]['leaguePoints'])
            winrate = "{:.2f}".format(100 * leagueEntryDTOs[0]['wins']/(leagueEntryDTOs[0]['losses']+leagueEntryDTOs[0]['wins']))
            wins = str(leagueEntryDTOs[0]['wins'])
            losses = str(leagueEntryDTOs[0]['losses'])
            file = discord.File("images/"+tier+".png",filename=tier+".png")
            embedVar = discord.Embed(color=EMBED_COLOR)
            embedVar.set_thumbnail(url="attachment://"+tier+".png")

            embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")

            embedVar.add_field(name="Solo/Duo Rank", value=tier+" "+rank+" "+lp +" LP", inline=False)
            embedVar.add_field(name="Winrate", value=winrate+"% ("+wins+"W  "+losses+ "L)",inline=False)
            # display users rank in embed message
            #embedVar.set_thumbnail(url="https://img.rankedboost.com/wp-content/uploads/2014/09/Season_2019_-_Challenger_1.png")
            await message.edit(content="",embed=embedVar,file=file)


"""
/flexrank [username]
- return 5x5 flex rank, wr,lp,etc for username
"""
@slash.slash(name="flexrank",
             description="View a summoner's flex 5v5 rank, lp, and ranked flex winrate.",
             options=[
             create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                create_choice(
                  name="NA",
                  value="NA"
                ),
                create_choice(
                  name="EUW",
                  value="EUW"
                ),
                create_choice(
                  name="EUNE",
                  value="EUNE"
                ),
                create_choice(
                  name="KR",
                  value="KR"
                ),
                create_choice(
                  name="OCE",
                  value="OCE"
                ),
                create_choice(
                  name="TR",
                  value="TR"
                ),
                create_choice(
                  name="JP",
                  value="JP"
                ),
                create_choice(
                  name="LAN",
                  value="LAN"
                ),
                create_choice(
                  name="LAS",
                  value="LAS"
                ),
                create_choice(
                  name="RU",
                  value="RU"
                ),
              ]),
               create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )
             ])
async def flexrank(ctx,username: str, region:str):
    sv4 = Summoner_v4(region)
    lv4 = League_v4(region)

    embed = discord.Embed(color=EMBED_COLOR,title="Fetching flex data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    else:
        # display loading gif while data is retrieved

        username = sv4.username_to_username(username)
        # check for successful request for league entries
        leagueEntryDTOs = lv4.get_ranked_leagues(encryptedSummonerID)
        if leagueEntryDTOs == -1:
            error_embed = discord.Embed(color=EMBED_COLOR,title=f"Error accessing Riot Games API. Please try again later.")
            await message.edit(content="",embed=error_embed)
            return

        # filter on flex queue
        leagueEntryDTOs = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_FLEX_SR"]
        if len(leagueEntryDTOs) == 0:
            error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username+" is not ranked in 5x5 flex for the current season.")
            await message.edit(content="",embed=error_embed)
            return
        else:
            # get data from dto and format into discord message
            tier = leagueEntryDTOs[0]['tier']
            rank = leagueEntryDTOs[0]['rank']
            lp = str(leagueEntryDTOs[0]['leaguePoints'])
            winrate = "{:.2f}".format(100 * leagueEntryDTOs[0]['wins']/(leagueEntryDTOs[0]['losses']+leagueEntryDTOs[0]['wins']))
            wins = str(leagueEntryDTOs[0]['wins'])
            losses = str(leagueEntryDTOs[0]['losses'])
            # message_string = ""+username+"\n"+tier+" " +rank + "\nLP: "+lp +"\nWinrate: " + winrate + "% ("+total_games+" games played)"
            file = discord.File("images/"+tier+".png",filename=tier+".png")
            embedVar = discord.Embed(color=EMBED_COLOR)
            embedVar.set_thumbnail(url="attachment://"+tier+".png")
            embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")
            embedVar.add_field(name="5x5 Flex Rank", value=tier+" "+rank+" "+lp +" LP", inline=False)
            embedVar.add_field(name="Winrate", value=winrate+"% ("+wins+"W  "+losses+ "L)",inline=False)
            # display users rank in embed message
            #embedVar.set_thumbnail(url="https://img.rankedboost.com/wp-content/uploads/2014/09/Season_2019_-_Challenger_1.png")
            await message.edit(content="",embed=embedVar,file=file)

"""
/free
- return free champion rotation
"""
@slash.slash(name="free",
             description="Get a list of free champions for this week, on a specified server.",
             options=[
              create_option(name="region",description="Region-specific server free champion rotation",option_type=3,required=True,choices=[
                 create_choice(
                   name="NA",
                   value="NA"
                 ),
                 create_choice(
                   name="EUW",
                   value="EUW"
                 ),
                 create_choice(
                   name="EUNE",
                   value="EUNE"
                 ),
                 create_choice(
                   name="KR",
                   value="KR"
                 ),
                 create_choice(
                   name="OCE",
                   value="OCE"
                 ),
                 create_choice(
                   name="TR",
                   value="TR"
                 ),
                 create_choice(
                   name="JP",
                   value="JP"
                 ),
                 create_choice(
                   name="LAN",
                   value="LAN"
                 ),
                 create_choice(
                   name="LAS",
                   value="LAS"
                 ),
                 create_choice(
                   name="RU",
                   value="RU"
                 ),
               ])]
             )
async def free(ctx,region:str):
    cv4 = Champion_v3(region)
    free_champions = cv4.get_free_champion_ids()
    if free_champions == -1:
        await ctx.send(f"Error accessing Riot Games API. Please try again later.")
        return

    embedVar = discord.Embed(color=EMBED_COLOR)
    champion_list = [CHAMPION_ID_TO_NAME[i] +'\n'for i in free_champions]
    embedVar.add_field(name="Current Free Champions ["+region+"]",value="".join(champion_list))
    await ctx.send(embed=embedVar)

"""
/tips [champion]
- Get tips for playing with and against a champion
"""
@slash.slash(name="tips",
             description="Get tips for playing with and against a champion.",
             options=[
                create_option(
                name="champion",
                description="champion name",
                option_type=3,
                required=True
                )
             ],
             )
async def tips(ctx,champion:str):
    # check that champion input is valid
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        await ctx.send(f"" + champion +" is not a valid champion name.")
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]

    # get tips from static datadragon that riot provides
    tips = get_champion_json(champion)
    if tips == -1:
        await ctx.send(f"Error retrieving champion tips from Riot Games. Try again later.")
        return

    embedVar = discord.Embed(color=EMBED_COLOR)
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+champion+".png")
    allytips = "".join([" -- "+i+'\n\n' for i in tips['data'][champion]['allytips']])
    enemytips = "".join([" -- "+i+'\n\n' for i in tips['data'][champion]['enemytips']])

    # some of the new champions dont have published tips yet.
    if len(allytips) == 0 or len(enemytips) == 0:
        await ctx.send(f"Riot games has not published tips for "+champion+" yet.")
        return

    embedVar.add_field(name="Tips for playing "+champion,value=allytips,inline=False)
    embedVar.add_field(name="\u200b",value="\u200b",inline=False)
    embedVar.add_field(name="Tips for playing against "+champion,value=enemytips,inline=False)

    await ctx.send(embed=embedVar)

"""
/abilities
- get a champion's description/ list of abilities
"""
@slash.slash(name="abilities",
             description="View a champion's abilities.",
             options=[
                create_option(
                name="champion",
                description="champion name",
                option_type=3,
                required=True
                )
             ]
            )
async def abilities(ctx,champion:str):
    # check that champion input is valid
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        await ctx.send(f"" + champion +" is not a valid champion name.")
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]

    # get tips from static datadragon that riot provides
    championInfo = get_champion_json(champion)
    if championInfo == -1:
        await ctx.send(f"Error retrieving champion info from Riot Games. Try again later.")
        return

    title = championInfo['data'][champion]['title']
    passive_name = championInfo['data'][champion]['passive']['name']
    passive_description = championInfo['data'][champion]['passive']['description']
    q_name = championInfo['data'][champion]['spells'][0]['name']
    q_description = championInfo['data'][champion]['spells'][0]['description']
    w_name = championInfo['data'][champion]['spells'][1]['name']
    w_description = championInfo['data'][champion]['spells'][1]['description']
    e_name = championInfo['data'][champion]['spells'][2]['name']
    e_description = championInfo['data'][champion]['spells'][2]['description']
    r_name = championInfo['data'][champion]['spells'][3]['name']
    r_description = championInfo['data'][champion]['spells'][3]['description']
    # lore = championInfo['data'][champion]['lore']

    embedVar = discord.Embed(color=EMBED_COLOR,title=champion+', '+title)
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+champion+".png")
    embedVar.add_field(name='Passive - ' + passive_name,value=passive_description,inline=False)
    embedVar.add_field(name='Q - '+q_name,value=q_description,inline=False)
    embedVar.add_field(name='W - '+w_name,value=w_description,inline=False)
    embedVar.add_field(name='E - '+e_name,value=e_description,inline=False)
    embedVar.add_field(name='R - '+r_name,value=r_description+'\n\n',inline=False)
    # embedVar.add_field(name='Lore',value=lore,inline=False)

    await ctx.send(embed=embedVar)

"""
/lore
- get lore description
"""
@slash.slash(name="lore",
             description="View a champion's lore.",
             options=[
                create_option(
                name="champion",
                description="champion name",
                option_type=3,
                required=True
                )
             ]
             )
async def lore(ctx,champion:str):
    # check that champion input is valid
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        await ctx.send(f"" + champion +" is not a valid champion name.")
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]

    # get tips from static datadragon that riot provides
    championInfo = get_champion_json(champion)
    if championInfo == -1:
        await ctx.send(f"Error retrieving champion info from Riot Games. Try again later.")
        return

    title = championInfo['data'][champion]['title']
    lore = championInfo['data'][champion]['lore']

    embedVar = discord.Embed(color=EMBED_COLOR,title=champion+', '+title)
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+champion+".png")
    embedVar.add_field(name='Lore',value=lore+'\n\n'+"To learn more about "+champion+', '+title+", visit the Riot Games Universe [website](https://universe.leagueoflegends.com/en_US/story/champion/"+champion+"/).",inline=False)

    await ctx.send(embed=embedVar)


"""
/livegame [username]
- live game info if available
"""
@slash.slash(name="livegame",
             description="Get live game data (if available) for the specified user.",
             options=[
             create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                create_choice(
                  name="NA",
                  value="NA"
                ),
                create_choice(
                  name="EUW",
                  value="EUW"
                ),
                create_choice(
                  name="EUNE",
                  value="EUNE"
                ),
                create_choice(
                  name="KR",
                  value="KR"
                ),
                create_choice(
                  name="OCE",
                  value="OCE"
                ),
                create_choice(
                  name="TR",
                  value="TR"
                ),
                create_choice(
                  name="JP",
                  value="JP"
                ),
                create_choice(
                  name="LAN",
                  value="LAN"
                ),
                create_choice(
                  name="LAS",
                  value="LAS"
                ),
                create_choice(
                  name="RU",
                  value="RU"
                ),
              ]),
               create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )])
async def livegame(ctx, username:str,region:str):
    spv4 = Spectator_v4(region)
    sv4 = Summoner_v4(region)
    lv4 = League_v4(region)

    embed = discord.Embed(color=EMBED_COLOR,title="Fetching live game data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    CurrentGameInfo = spv4.get_active_game(sv4.username_to_encryptedSummonerID(username))
    profileIconId = sv4.username_to_profileIconId(username)
    if CurrentGameInfo == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username+" is not currently in a game.")
        await message.edit(content="",embed=error_embed)
        return


    username = sv4.username_to_username(username)
    # title is map, game mode and time elapsed
    embedVar = discord.Embed(color=EMBED_COLOR,title=MAP_ID_TO_NAME[CurrentGameInfo['mapId']]+" | "+QUEUE_ID_TO_NAME[CurrentGameInfo['gameQueueConfigId']]+' | '+ format_seconds(CurrentGameInfo['gameLength']))

    # get users profile pic and display
    embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")
    participants = CurrentGameInfo['participants']

    # display members of blue and red teams by position and champion
    blue_team_users = [i['summonerId'] for i in participants if i['teamId'] == BLUE_TEAM_ID]
    blue_team_ranks = {}
    for i in blue_team_users:
        leagueEntryDTOs = lv4.get_ranked_leagues(i)
        if leagueEntryDTOs == -1:
            error_embed = discord.Embed(color=EMBED_COLOR,title=f"Error accessing Riot Games API. Please try again later.")
            await message.edit(content="",embed=error_embed)
            return
        else:
            # filter on gamequeue
            if QUEUE_ID_TO_NAME[CurrentGameInfo['gameQueueConfigId']] == "5v5 Ranked Flex games":
                target_queue = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_FLEX_SR"]
                if len(target_queue) == 0:
                    blue_team_ranks[i] = "UNRANKED"
                else:
                    blue_team_ranks[i] = target_queue[0]['tier']+" "+target_queue[0]['rank']
            else:
                target_queue = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_SOLO_5x5"]
                if len(target_queue) == 0:
                    blue_team_ranks[i] = "UNRANKED"
                else:
                    blue_team_ranks[i] = target_queue[0]['tier']+" "+target_queue[0]['rank']


    red_team_users = [i['summonerId'] for i in participants if i['teamId'] == RED_TEAM_ID]
    red_team_ranks = {}
    for i in red_team_users:
        leagueEntryDTOs = lv4.get_ranked_leagues(i)
        if leagueEntryDTOs == -1:
            error_embed = discord.Embed(color=EMBED_COLOR,title=f"Error accessing Riot Games API. Please try again later.")
            await message.edit(content="",embed=error_embed)
            return
        else:
            # filter on gamequeue
            if QUEUE_ID_TO_NAME[CurrentGameInfo['gameQueueConfigId']] == "5v5 Ranked Flex games":
                target_queue = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_FLEX_SR"]
                if len(target_queue) == 0:
                    red_team_ranks[i] = "UNRANKED"
                else:
                    red_team_ranks[i] = target_queue[0]['tier']+" "+target_queue[0]['rank']
            else:
                target_queue = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_SOLO_5x5"]
                if len(target_queue) == 0:
                    red_team_ranks[i] = "UNRANKED"
                else:
                    red_team_ranks[i] = target_queue[0]['tier']+" "+target_queue[0]['rank']



    embedVar.add_field(name="Username",value="".join([i['summonerName']+'\n' for i in participants if i['teamId']==BLUE_TEAM_ID]),inline=True)
    embedVar.add_field(name="Champion",value="".join([CHAMPION_ID_TO_NAME[i['championId']]+'\n' for i in participants if i['teamId']==BLUE_TEAM_ID]),inline=True)
    embedVar.add_field(name="Rank",value="".join([blue_team_ranks[i['summonerId']] +'\n' for i in participants if i['teamId']==BLUE_TEAM_ID]),inline=True)
    #embedVar.add_field(name="Red Team",value="".join(red_team_str),inline=False)
    embedVar.add_field(name="Username",value="".join([i['summonerName']+'\n' for i in participants if i['teamId']==RED_TEAM_ID]),inline=True)
    embedVar.add_field(name="Champion",value="".join([CHAMPION_ID_TO_NAME[i['championId']]+'\n' for i in participants if i['teamId']==RED_TEAM_ID]),inline=True)
    embedVar.add_field(name="Rank",value="".join([red_team_ranks[i['summonerId']] +'\n' for i in participants if i['teamId']==RED_TEAM_ID]),inline=True)

    # display user's champion as thumbnail
    participants = CurrentGameInfo['participants']
    championId = [i['championId'] for i in participants if i['summonerName'].lower() == username.lower()][0]
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+CHAMPION_ID_TO_NAME[championId]+".png")
    await message.edit(content="",embed=embedVar)


"""
/mastery [username] [champion]
- display a formatted discord message regarding masteries returned by https://developer.riotgames.com/apis#champion-mastery-v4
"""
@slash.slash(name="mastery",
             description="View a player's mastery score for a specific champion.",
             options=[
               create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                  create_choice(
                    name="NA",
                    value="NA"
                  ),
                  create_choice(
                    name="EUW",
                    value="EUW"
                  ),
                  create_choice(
                    name="EUNE",
                    value="EUNE"
                  ),
                  create_choice(
                    name="KR",
                    value="KR"
                  ),
                  create_choice(
                    name="OCE",
                    value="OCE"
                  ),
                  create_choice(
                    name="TR",
                    value="TR"
                  ),
                  create_choice(
                    name="JP",
                    value="JP"
                  ),
                  create_choice(
                    name="LAN",
                    value="LAN"
                  ),
                  create_choice(
                    name="LAS",
                    value="LAS"
                  ),
                  create_choice(
                    name="RU",
                    value="RU"
                  ),
                ]),
               create_option(name="username",description="Summoner Name",option_type=3,required=True),
               create_option(name="champion",description="Name of the champion",option_type=3,required=True)])
async def mastery(ctx, username:str,champion:str,region:str):
    embed = discord.Embed(color=EMBED_COLOR,title="Fetching mastery data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    cm4 = Champion_mastery_v4(region)
    sv4 = Summoner_v4(region)

    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)

    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    username = sv4.username_to_username(username)
    #check champion input
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"" + champion +" is not a valid champion name.")
        await message.edit(content="",embed=error_embed)
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]
    mastery_dto = cm4.get_individual_champion_mastery(encryptedSummonerID,CHAMPION_NAME_TO_ID[champion.lower()])
    if mastery_dto == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username+" has no available mastery data for "+champion)
        await message.edit(content="",embed=error_embed)
        return


    embedVar = discord.Embed(color=EMBED_COLOR)

    # double dictionary lookup to ensure URL has upper/lowercasing consistent with riots api, regardless of user input
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+champion+".png")
    embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")
    embedVar.add_field(name=champion,value=str(mastery_dto['championPoints'])+" points",inline=False)

    # convert from ms to s
    embedVar.add_field(name="Last Played",value=str(datetime.datetime.utcfromtimestamp(mastery_dto['lastPlayTime']/1000)),inline=True)

    # display png of mastery at bototm
    file = discord.File("images/mastery-"+str(mastery_dto['championLevel'])+".png",filename="mastery-"+str(mastery_dto['championLevel'])+".png")
    embedVar.set_image(url="attachment://mastery-"+str(mastery_dto['championLevel'])+".png")
    await message.edit(embed=embedVar,file=file)

"""
/topmastery
- View a user's top 10 champions by mastery points.
"""
@slash.slash(name="topmastery",
             description="View a user's top 10 champions by mastery points.",
             options=[
               create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                  create_choice(
                    name="NA",
                    value="NA"
                  ),
                  create_choice(
                    name="EUW",
                    value="EUW"
                  ),
                  create_choice(
                    name="EUNE",
                    value="EUNE"
                  ),
                  create_choice(
                    name="KR",
                    value="KR"
                  ),
                  create_choice(
                    name="OCE",
                    value="OCE"
                  ),
                  create_choice(
                    name="TR",
                    value="TR"
                  ),
                  create_choice(
                    name="JP",
                    value="JP"
                  ),
                  create_choice(
                    name="LAN",
                    value="LAN"
                  ),
                  create_choice(
                    name="LAS",
                    value="LAS"
                  ),
                  create_choice(
                    name="RU",
                    value="RU"
                  ),
                ]),
               create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )])
async def topmastery(ctx,username:str,region:str):
    embed = discord.Embed(color=EMBED_COLOR,title="Fetching mastery data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    cm4 = Champion_mastery_v4(region)
    sv4 = Summoner_v4(region)

    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)

    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    username = sv4.username_to_username(username)

    top_10 = cm4.get_all_champion_mastery(encryptedSummonerID)

    if top_10 == -1 or len(top_10) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"Champion mastery data for "+username+" could not be retrieved.")
        await message.edit(content="",embed=error_embed)
        return

    if len(top_10) > 10:
        top_10 = top_10[:10]

    champion_str = ""
    point_str = ""
    mastery_str = ""
    for i in top_10:
        champion_str += CHAMPION_ID_TO_NAME[i['championId']] +'\n'
        point_str += str(i['championPoints']) + " pts\n"
        mastery_str += 'Level '+str(i['championLevel'])+'\n'

    embedVar = discord.Embed(color=EMBED_COLOR,title="Top 10 Mastered Champions")
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+CHAMPION_ID_TO_NAME[top_10[0]['championId']]+".png")
    embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")
    embedVar.add_field(name="Champion",value=champion_str,inline=True)
    embedVar.add_field(name="Points",value=point_str,inline=True)
    embedVar.add_field(name="Mastery",value=mastery_str,inline=True)

    await message.edit(embed=embedVar)

"""
/championstats [username] [champion] [queue]
- cs, kda, w/r etc. on a specific champion, in a selected game queue
"""
@slash.slash(name="championstats",
             description="View a user's KD/A, win rate, damage and other stats on a specific champion.",
             options=[
             create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                create_choice(
                  name="NA",
                  value="NA"
                ),
                create_choice(
                  name="EUW",
                  value="EUW"
                ),
                create_choice(
                  name="EUNE",
                  value="EUNE"
                ),
                create_choice(
                  name="KR",
                  value="KR"
                ),
                create_choice(
                  name="OCE",
                  value="OCE"
                ),
                create_choice(
                  name="TR",
                  value="TR"
                ),
                create_choice(
                  name="JP",
                  value="JP"
                ),
                create_choice(
                  name="LAN",
                  value="LAN"
                ),
                create_choice(
                  name="LAS",
                  value="LAS"
                ),
                create_choice(
                  name="RU",
                  value="RU"
                ),
              ]),
               create_option(name="username",description="Summoner Name",option_type=3,required=True),
               create_option(name="champion",description="Name of the champion",option_type=3,required=True),
               create_option(name="queue",description="Summoner's rift queue type",option_type=4,required=True, choices=[
                  create_choice(
                    name="5v5 Ranked Solo",
                    value=QUEUE_NAME_TO_ID["5v5 Ranked Solo games"]
                  ),
                  create_choice(
                    name="5v5 Ranked Flex",
                    value=QUEUE_NAME_TO_ID["5v5 Ranked Flex games"]
                  ),
                  create_choice(
                    name="5v5 Blind Pick",
                    value=QUEUE_NAME_TO_ID["5v5 Blind Pick games"]
                  ),
                  create_choice(
                    name="5v5 Draft Pick",
                    value=QUEUE_NAME_TO_ID["5v5 Draft Pick games"]
                  ),
                  create_choice(
                    name="All queues",
                    value=0
                  )
                ])
               ])
async def championstats(ctx,region:str,username:str,champion:str,queueId:int):
    embed = discord.Embed(color=EMBED_COLOR,title="Fetching newest data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    sv4 = Summoner_v4(region)
    mv5 = Match_v5(region)

    encryptedAccountID = sv4.username_to_encryptedAccountID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    if encryptedAccountID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    username = sv4.username_to_username(username)
    #check champion input
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"" + champion +" is not a valid champion name.")
        await message.edit(content="",embed=error_embed)
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]

    # display loading gif while data is retrieved
    rdf = get_matches_from_db(encryptedAccountID,mv5,sv4)
    if len(rdf) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"" + "Could not find current season match data for "+username)
        await message.edit(content="",embed=error_embed)
        return

    if queueId != 0:
        rdf = rdf[rdf['queueId']==queueId]

    queueName = get_queue_name(queueId)

    # empty match history for queue case
    if len(rdf) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username+" has not played any "+queueName+" this season.")
        await message.edit(content="",embed=error_embed)
        return

    # apply filters at the bitter end!
    rdf = rdf[rdf['championName'] == champion]
    if len(rdf) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"" + "Could not find current season match data for "+username+" on "+champion)
        await message.edit(content="",embed=error_embed)
        return


    df = rdf.groupby(['championName']).mean()



    embedVar = discord.Embed(color=EMBED_COLOR,title=champion + " Stats ["+queueName+"]")
    # double dictionary lookup to ensure URL has upper/lowercasing consistent with riots api, regardless of user input
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+champion+".png")
    embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")

    embedVar.add_field(name='Kills',value="{:.2f}".format(df['kills'][0]),inline=True)
    embedVar.add_field(name='Deaths',value="{:.2f}".format(df['deaths'][0]),inline=True)
    embedVar.add_field(name='Assists',value="{:.2f}".format(df['assists'][0]),inline=True)

    embedVar.add_field(name='K/DA',value=kda(df['kills'][0],df['deaths'][0],df['assists'][0]),inline=True)
    embedVar.add_field(name='Winrate',value="{:.2f}%".format(df['win'][0]*100),inline=True)
    numWins = sum(rdf['win'])
    embedVar.add_field(name='Games played',value=str(len(rdf)) + " ("+str(numWins)+"W "+str(len(rdf)-numWins)+"L)",inline=True)

    embedVar.add_field(name='Total CS',value="{:.2f}".format(df['CS'][0]),inline=True)
    embedVar.add_field(name='CS/min',value="{:.2f}".format(df['CS/min'][0]),inline=True)
    embedVar.add_field(name='Gold Earned',value="{:.2f}".format(df['goldEarned'][0]),inline=True)

    embedVar.add_field(name='Damage Dealt',value="{:.2f}".format(df['totalDamageDealtToChampions'][0]),inline=True)
    embedVar.add_field(name='Damage Taken',value="{:.2f}".format(df['totalDamageTaken'][0]),inline=True)
    embedVar.add_field(name='First Blood %',value="{:.2f}".format(df['firstBlood'][0] * 100),inline=True)

    await message.edit(content="",embed=embedVar)


@slash.slash(name="duostats",
             description="View a duo's w/r, games played, and their most common champion pairings and stats.",
             options=[
             create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                create_choice(
                  name="NA",
                  value="NA"
                ),
                create_choice(
                  name="EUW",
                  value="EUW"
                ),
                create_choice(
                  name="EUNE",
                  value="EUNE"
                ),
                create_choice(
                  name="KR",
                  value="KR"
                ),
                create_choice(
                  name="OCE",
                  value="OCE"
                ),
                create_choice(
                  name="TR",
                  value="TR"
                ),
                create_choice(
                  name="JP",
                  value="JP"
                ),
                create_choice(
                  name="LAN",
                  value="LAN"
                ),
                create_choice(
                  name="LAS",
                  value="LAS"
                ),
                create_choice(
                  name="RU",
                  value="RU"
                ),
              ]),
               create_option(name="username1",description="Summoner Name",option_type=3,required=True),
               create_option(name="username2",description="Summoner Name",option_type=3,required=True),
               create_option(name="queue",description="Summoner's rift queue type",option_type=4,required=True, choices=[
                  create_choice(
                    name="5v5 Ranked Solo",
                    value=QUEUE_NAME_TO_ID["5v5 Ranked Solo games"]
                  ),
                  create_choice(
                    name="5v5 Ranked Flex",
                    value=QUEUE_NAME_TO_ID["5v5 Ranked Flex games"]
                  ),
                  create_choice(
                    name="5v5 Blind Pick",
                    value=QUEUE_NAME_TO_ID["5v5 Blind Pick games"]
                  ),
                  create_choice(
                    name="5v5 Draft Pick",
                    value=QUEUE_NAME_TO_ID["5v5 Draft Pick games"]
                  ),
                  create_choice(
                    name="All queues",
                    value=0
                  )
                ])
               ])
async def duostats(ctx,region:str,username1:str,username2:str,queueId:int):
    embed = discord.Embed(color=EMBED_COLOR,title="Fetching newest data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    sv4 = Summoner_v4(region)
    mv5 = Match_v5(region)

    encryptedAccountID = sv4.username_to_encryptedAccountID(username1)
    profileIconId = sv4.username_to_profileIconId(username1)

    # check if username1 is valid input
    if encryptedAccountID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username1+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    username = sv4.username_to_username(username1)

    #check if username2 is valid input
    duo_encryptedAccountID = sv4.username_to_encryptedAccountID(username2)
    if duo_encryptedAccountID == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username2+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    duo_username = sv4.username_to_username(username2)

    # convert queueId into readable string
    queueName = get_queue_name(queueId)

    # get match history for both users, then inner join on common games
    df1 = get_matches_from_db(encryptedAccountID,mv5,sv4)
    df2 = get_matches_from_db(duo_encryptedAccountID,mv5,sv4)

    # no match history edge case
    if len(df1) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"Could not retrieve match history for "+username1)
        await message.edit(content="",embed=error_embed)
        return

    # no match history for DUO edge case
    if len(df2) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"Could not retrieve match history for "+username2)
        await message.edit(content="",embed=error_embed)
        return

    # inner join on two users common games
    duo_df = df1.join(df2.set_index('gameId'),on='gameId',how="inner",rsuffix="_duo")

    # if a queueId is specified, filter on that queue
    if queueId != 0:
        duo_df = duo_df[duo_df['queueId'] == queueId]
    # case where the users never played together
    if len(duo_df) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username1+" has not played any "+queueName+" with "+username2+" this season.")
        await message.edit(content="",embed=error_embed)
        return


    embedVar = discord.Embed(color=EMBED_COLOR,title=username2+" Duo Stats ["+queueName+"]")
    embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")

    # WR and total games played
    wr = duo_df['win'].mean()
    total_game_count = duo_df['win'].count()

    embedVar.add_field(name='Total Games Played',value=str(total_game_count)+'\n ',inline=True)
    embedVar.add_field(name='Overall Winrate',value="{:.2f}%".format(wr*100),inline=True)

    # top 5 most played + WR
    # specify Username,champion,role
    duo_grouped = duo_df.groupby(['championName','championName_duo']).count().sort_values('win_duo',ascending=False)
    if len(duo_grouped) > 10:
        duo_grouped = duo_grouped[:10]

    top10 =  duo_grouped.index.values
    pair_game_counts = duo_grouped['win'].values

    # compute statistics for each of the top 5 pairings and put together formatted string to display
    idx = 0
    user1_string = ""
    user2_string = ""
    wr_string = ""
    for i,j in top10:
        tmp = duo_df[(duo_df['championName']==i)& (duo_df['championName_duo']==j)]
        lane1 = lane(tmp['lane'].value_counts().index[0],tmp['role'].value_counts().index[0])
        lane2 = lane(tmp['lane_duo'].value_counts().index[0],tmp['role_duo'].value_counts().index[0])
        numWins = sum(tmp['win'])
        total_games = str(len(tmp)) + " ("+str(numWins)+"W "+str(len(tmp)-numWins)+"L) "
        winrate = "{:.2f}%".format(tmp['win'].mean() * 100)

        user1_string += i+' ('+lane1+')\n'
        user2_string += j+' ('+lane2+')\n'
        wr_string += total_games+winrate+'\n'
        #pair_string += f"{i:<12}{'('+lane1+')':<9}{' +  '+j:<16}{'('+lane2+')':<9}{total_games+winrate:<25}" +'\n'
        idx += 1

    embedVar.add_field(name='Most Common Champion Pairings:',value='\u200b',inline=False)
    embedVar.add_field(name=username1,value=user1_string,inline=True)
    embedVar.add_field(name=username2,value=user2_string,inline=True)
    embedVar.add_field(name='Games played/Winrate',value=wr_string,inline=True)
    await message.edit(content="",embed=embedVar)

"""
/mostplayed [username] [queue]
- View a user's top 10 most played champions + stats for a selected game queue.
"""
@slash.slash(name="mostplayed",
             description="View stats for user's top 10 most played champions in a selected game queue.",
             options=[
             create_option(name="region",description="Region-specific server that the user plays on.",option_type=3,required=True,choices=[
                create_choice(
                  name="NA",
                  value="NA"
                ),
                create_choice(
                  name="EUW",
                  value="EUW"
                ),
                create_choice(
                  name="EUNE",
                  value="EUNE"
                ),
                create_choice(
                  name="KR",
                  value="KR"
                ),
                create_choice(
                  name="OCE",
                  value="OCE"
                ),
                create_choice(
                  name="TR",
                  value="TR"
                ),
                create_choice(
                  name="JP",
                  value="JP"
                ),
                create_choice(
                  name="LAN",
                  value="LAN"
                ),
                create_choice(
                  name="LAS",
                  value="LAS"
                ),
                create_choice(
                  name="RU",
                  value="RU"
                ),
              ]),
               create_option(name="username",description="Summoner Name",option_type=3,required=True),
               create_option(name="queue",description="Summoner's rift queue type",option_type=4,required=True, choices=[
                  create_choice(
                    name="5v5 Ranked Solo",
                    value=QUEUE_NAME_TO_ID["5v5 Ranked Solo games"]
                  ),
                  create_choice(
                    name="5v5 Ranked Flex",
                    value=QUEUE_NAME_TO_ID["5v5 Ranked Flex games"]
                  ),
                  create_choice(
                    name="5v5 Blind Pick",
                    value=QUEUE_NAME_TO_ID["5v5 Blind Pick games"]
                  ),
                  create_choice(
                    name="5v5 Draft Pick",
                    value=QUEUE_NAME_TO_ID["5v5 Draft Pick games"]
                  ),
                  create_choice(
                    name="All queues",
                    value=0
                  )
                ])
               ])
async def mostplayed(ctx,region:str,username:str,queueId:int):
    embed = discord.Embed(color=EMBED_COLOR,title="Fetching newest data...")
    embed.set_image(url="https://64.media.tumblr.com/e59ffcaa310835f2b207bebcf96258d0/f75a4d609d3d34a7-ba/s640x960/397ef2eb12b0750f1dfcecce54ac41ac6299f79e.gif")
    message = await ctx.send(embed=embed)

    sv4 = Summoner_v4(region)
    mv5 = Match_v5(region)

    encryptedAccountID = sv4.username_to_encryptedAccountID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    if encryptedAccountID == -1 or profileIconId == -1:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"The username "+username+" could not be found.")
        await message.edit(content="",embed=error_embed)
        return
    username = sv4.username_to_username(username)

    # get match data from database
    df = get_matches_from_db(encryptedAccountID,mv5,sv4)
    if len(df) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f"" + "Could not find current season match data for "+username)
        await message.edit(content="",embed=error_embed)
        return

    # filter if queue is specified
    if queueId != 0:
        df = df[df['queueId']==queueId]
    queueName = get_queue_name(queueId)

    # empty match history for queue case
    if len(df) == 0:
        error_embed = discord.Embed(color=EMBED_COLOR,title=f""+username+" has not played any "+queueName+" this season.")
        await message.edit(content="",embed=error_embed)
        return

    # group by champion to find top 10 most played.
    grouped = df.groupby(['championName']).count().sort_values('win',ascending=False)
    if len(grouped) > 10:
        grouped = grouped[:10]

    # top 10 - champion names and respective # games played
    top10 = grouped.index.values
    game_counts = grouped['win'].values

    # compute statistics for each of the top 10 pairings and put together formatted string to display
    idx = 0
    champion_str = ""
    games_played_str = ""
    kda_str = ""
    for i in top10:
        tmp = df[df['championName'] == i]
        champion_str += i + '\n'
        numWins = sum(tmp['win'])
        gdf = tmp.groupby(['championName']).mean()
        kda_str += kda(gdf['kills'][0],gdf['deaths'][0],gdf['assists'][0]) + '\n'
        games_played_str += str(len(tmp)) + " ("+str(numWins)+"W "+str(len(tmp)-numWins)+"L) "+"{:.2f}%".format(gdf['win'][0] * 100) + '\n'
        idx += 1

    embedVar = discord.Embed(color=EMBED_COLOR,title="Top 10 played champions in "+queueName)
    # double dictionary lookup to ensure URL has upper/lowercasing consistent with riots api, regardless of user input
    embedVar.set_thumbnail(url=DD_BASE_URL+"/img/champion/"+top10[0]+".png")
    embedVar.set_author(name=username,icon_url=DD_BASE_URL+"/img/profileicon/"+str(profileIconId)+".png")

    embedVar.add_field(name="Champion",value=champion_str,inline=True)
    embedVar.add_field(name="K/DA",value=kda_str,inline=True)
    embedVar.add_field(name="Games played/Winrate",value=games_played_str,inline=True)

    await message.edit(content="",embed=embedVar)
"""
Helper method that retrieved matches played from the database, and gets
new matches from the riot games api when necessary.

Takes accountId, and region specific api objects
Returns a dataframe, where each row is a user's stats from a specific match.
"""
def get_matches_from_db(encryptedAccountID,mv,sv4):
    # Generate unix timestamp for 01/01/Current Year (LoL season start apprx.)
    year = datetime.date.today().year
    date = datetime.datetime(year, 1, 1)
    NEW_YEAR_TIME_STAMP = date.timestamp()

    # request username and check for valid response
    username = sv4.encryptedAccountID_to_username(encryptedAccountID)
    puuid = sv4.username_to_puuid(username)
    total = 0
    beginIndex= 0
    objects = []

    # find timestamp for most recent game stored in db. Only request riot api for
    # games that occured after this timestamp
    mostRecentGame = db.matches.find({'puuid':puuid}).sort("timestamp",-1)
    mostRecentTimestamp = None
    if db.matches.count_documents({'puuid':puuid}) != 0:
        mostRecentTimestamp = mostRecentGame[0]['timestamp']

    while True:
        #get match list for 100 game window (max allowed by riot api) and check for valid response
        matchList = mv.get_match_list(puuid,start=beginIndex,count=100)

        #check if d == -1
        if matchList == -1:
            # DISCORD MESSAGE HERE
            print("Could not retrieve match data for "+username)
            return pd.DataFrame()
        elif len(matchList) == 0:
            break

        #get list of matchDtos from api response d
        for id in matchList:
            # MAKE REQUEST GETMATCH and check for valid response
            match = mv.get_match(id)
            print(id)

            if match == -1:
                if len(objects) > 0:
                    break
                else:
                    return pd.DataFrame()


            # only process matches in current season (year)
            if match['gameCreation']/1000 <= NEW_YEAR_TIME_STAMP: #conversion from ms to s
                break

            #exclude remake case (disconnected game less than 240 seconds)
            if match['gameDuration'] < 240:
                continue

            # only request matches from riot api for matches not in db
            if mostRecentTimestamp != None and match['gameCreation'] <= mostRecentTimestamp:
                break
            else:
                player_stats = None
                for j in match['participants']:
                    if j['puuid'] == puuid:
                        player_stats = j

                d = {
                    "puuid":puuid,
                    "username":username,
                    "gameId":id,
                    "queueId":match['queueId'],
                    "championId":player_stats['championId'],
                    "championName":player_stats['championName'],
                    "lane":player_stats['lane'],
                    "role":player_stats['role'],
                    "timestamp":match['gameCreation'],
                    "CS":player_stats['totalMinionsKilled']+player_stats['neutralMinionsKilled'],
                    "CS/min":(player_stats['totalMinionsKilled']+player_stats['neutralMinionsKilled'] )/(player_stats['timePlayed']/60),
                    "kills":player_stats['kills'],
                    "deaths":player_stats['deaths'],
                    "assists":player_stats['assists'],
                    "goldEarned":player_stats['goldEarned'],
                    "totalDamageDealtToChampions":player_stats['totalDamageDealtToChampions'],
                    "damageDealtToObjectives":player_stats['damageDealtToObjectives'],
                    "totalDamageTaken":player_stats['totalDamageTaken'],
                    "firstBlood":player_stats['firstBloodKill'],
                    "firstBloodAssist":player_stats['firstBloodAssist'],
                    "win":player_stats['win']
                }
                objects.append(d)

        beginIndex += 100

    if len(objects)>0:
        db.matches.insert_many(objects)

    df = pd.DataFrame(list(db.matches.find({'puuid':puuid})))
    return df


def get_queue_name(queueId):
    queueName = None
    if queueId != 0:
        return QUEUE_ID_TO_NAME[queueId]
    else:
        return "All Queues"

def format_seconds(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return "%02d:%02d" % (minutes,seconds)

def kda(kills,deaths,assists):
    if deaths == 0:
        return 'Perfect K/DA'
    else:
        return "{:.2f}".format((kills+assists)/deaths)

"""
{
    (MID_LANE, SOLO): MIDDLE,
    (TOP_LANE, SOLO): TOP,
    (JUNGLE, NONE): JUNGLE,
    (BOT_LANE, DUO_CARRY): BOTTOM,
    (BOT_LANE, DUO_SUPPORT): UTILITY
}
"""
def lane(lane,role):
    if lane == "MIDDLE":
        return "MID"
    if lane == "TOP":
        return lane
    if lane == "JUNGLE":
        return lane
    if lane =="BOTTOM" and role=="CARRY":
        return "ADC"
    else:
        return "SUPPORT"

BOT_TOKEN = os.environ['BOT_TOKEN']
client.run(BOT_TOKEN)
