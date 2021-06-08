import discord
import os
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

from src.api.summoner_v4 import Summoner_v4
from src.api.league_v4 import League_v4
from src.api.champion_v3 import Champion_v3
from src.api.spectator_v4 import Spectator_v4
from src.api.match_v4 import Match_v4
from src.api.champion_mastery_v4 import Champion_mastery_v4

from data_dragon import CHAMPION_ID_TO_NAME
from data_dragon import CHAMPION_NAME_TO_ID
from data_dragon import QUEUE_ID_TO_NAME
from data_dragon import QUEUE_NAME_TO_ID
from data_dragon import MAP_ID_TO_NAME
from data_dragon import BLUE_TEAM_ID,RED_TEAM_ID


import datetime
import pandas as pd
import numpy
import time

# MongoDB Atlas
import pymongo

db_token = os.getenv('DB_TOKEN')
client = pymongo.MongoClient("mongodb+srv://sdogaru:"+db_token+"@matches.vs94y.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.AhriBot

intents = discord.Intents(messages=True, guilds=True)
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

enabled = True

# classes for accessing riot games api
sv4 = Summoner_v4()
lv4 = League_v4()
cv4 = Champion_v3()
spv4 = Spectator_v4()
mv4 = Match_v4()
cm4 = Champion_mastery_v4()

"""
When the bot is added to a server, send a gif in chat to introduce
"""
@client.event
async def on_guild_join(guild):
    #general = discord.utils.find(lambda x: x.name == 'general',  guild.text_channels)
    if len(guild.text_channels) > 1: #general:
        await guild.text_channels[0].send(file=discord.File('ahri_gif.gif'))
        await guild.text_channels[0].send("Hi, I'm Ahri - a Discord bot for all things League of Legends! To get started, type /")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global enabled

    if message.author == client.user:
        return


guild_ids = [722714561136033804]

"""
/rank [username]
- returns rank, lp, and winrate for username
"""
@slash.slash(name="rank",
             description="View a summoner's soloq rank, lp, and winrate.",
             options=[
               create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )
             ], guild_ids=guild_ids)
async def rank(ctx,username: str):
    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1 or profileIconId == -1:
        await ctx.send(f"The username "+username+" could not be found.")
        return
    else:
        username = sv4.username_to_username(username)
        # check for successful request for league entries
        leagueEntryDTOs = lv4.get_ranked_leagues(encryptedSummonerID)
        if leagueEntryDTOs == -1:
            await ctx.send(f"Error accessing Riot Games API. Please try again later.")
            return

        # filter on soloqueue
        leagueEntryDTOs = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_SOLO_5x5"]
        if len(leagueEntryDTOs) == 0:
            await ctx.send(f""+username+" is not ranked in soloqueue for the current season.")
            return
        else:
            # get data from dto and format into discord message
            tier = leagueEntryDTOs[0]['tier']
            rank = leagueEntryDTOs[0]['rank']
            lp = str(leagueEntryDTOs[0]['leaguePoints'])
            winrate = str(100 * leagueEntryDTOs[0]['wins']/(leagueEntryDTOs[0]['losses']+leagueEntryDTOs[0]['wins']))[:5]
            wins = str(leagueEntryDTOs[0]['wins'])
            losses = str(leagueEntryDTOs[0]['losses'])
            # message_string = ""+username+"\n"+tier+" " +rank + "\nLP: "+lp +"\nWinrate: " + winrate + "% ("+total_games+" games played)"
            file = discord.File("images/"+tier+".png",filename=tier+".png")
            embedVar = discord.Embed(color=0x9932CC)
            embedVar.set_thumbnail(url="attachment://"+tier+".png")
            embedVar.set_author(name=username,icon_url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/"+str(profileIconId)+".png")
            embedVar.add_field(name="Solo/Duo Rank", value=tier+" "+rank+" "+lp +" LP", inline=False)
            embedVar.add_field(name="Winrate", value=winrate+"% ("+wins+"W  "+losses+ "L)",inline=False)
            # display users rank in embed message
            #embedVar.set_thumbnail(url="https://img.rankedboost.com/wp-content/uploads/2014/09/Season_2019_-_Challenger_1.png")
            await ctx.send(file=file,embed=embedVar)


@slash.slash(name="flexrank",
             description="View a summoner's flex 5v5 rank, lp, and winrate.",
             options=[
               create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )
             ], guild_ids=guild_ids)
async def flexrank(ctx,username: str):
    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1:
        await ctx.send(f"The username "+username+" could not be found.",hidden=True,file=file)
        return
    else:
        username = sv4.username_to_username(username)
        # check for successful request for league entries
        leagueEntryDTOs = lv4.get_ranked_leagues(encryptedSummonerID)
        if leagueEntryDTOs == -1:
            await ctx.send(f"Error accessing Riot Games API. Please try again later.")
            return

        # filter on flex queue
        leagueEntryDTOs = [i for i in leagueEntryDTOs if i['queueType'] == "RANKED_FLEX_SR"]
        if len(leagueEntryDTOs) == 0:
            await ctx.send(f""+username+" is not ranked in 5x5 flex for the current season.")
            return
        else:
            # get data from dto and format into discord message
            tier = leagueEntryDTOs[0]['tier']
            rank = leagueEntryDTOs[0]['rank']
            lp = str(leagueEntryDTOs[0]['leaguePoints'])
            winrate = str(100 * leagueEntryDTOs[0]['wins']/(leagueEntryDTOs[0]['losses']+leagueEntryDTOs[0]['wins']))[:5]
            wins = str(leagueEntryDTOs[0]['wins'])
            losses = str(leagueEntryDTOs[0]['losses'])
            # message_string = ""+username+"\n"+tier+" " +rank + "\nLP: "+lp +"\nWinrate: " + winrate + "% ("+total_games+" games played)"
            file = discord.File("images/"+tier+".png",filename=tier+".png")
            embedVar = discord.Embed(color=0x9932CC)
            embedVar.set_thumbnail(url="attachment://"+tier+".png")
            embedVar.set_author(name=username,icon_url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/"+str(profileIconId)+".png")
            embedVar.add_field(name="5x5 Flex Rank", value=tier+" "+rank+" "+lp +" LP", inline=False)
            embedVar.add_field(name="Winrate", value=winrate+"% ("+wins+"W  "+losses+ "L)",inline=False)
            # display users rank in embed message
            #embedVar.set_thumbnail(url="https://img.rankedboost.com/wp-content/uploads/2014/09/Season_2019_-_Challenger_1.png")
            await ctx.send(file=file,embed=embedVar)

@slash.slash(name="freechamps",
             description="Get a list of free champions for this week.",
             guild_ids=guild_ids)
async def freechamps(ctx):
    free_champions = cv4.get_free_champion_ids()
    if free_champions == -1:
        await ctx.send(f"Error accessing Riot Games API. Please try again later.")
        return

    embedVar = discord.Embed(color=0x9932CC)
    champion_list = [CHAMPION_ID_TO_NAME[i] +'\n'for i in free_champions]
    embedVar.add_field(name="Current Free Champions:",value="".join(champion_list))
    await ctx.send(embed=embedVar)



@slash.slash(name="livegame",
             description="Get live game data (if available) for the specified user.",
             options=[
               create_option(
                 name="username",
                 description="Summoner Name",
                 option_type=3,
                 required=True
               )],guild_ids=guild_ids)
async def livegame(ctx, username:str):
    CurrentGameInfo = spv4.get_active_game(sv4.username_to_encryptedSummonerID(username))
    profileIconId = sv4.username_to_profileIconId(username)
    if CurrentGameInfo == -1 or profileIconId == -1:
        await ctx.send(f""+username+" is not currently in a game.")
        return
    username = sv4.username_to_username(username)
    # title is map, game mode and time elapsed
    embedVar = discord.Embed(color=0x9932CC,title=MAP_ID_TO_NAME[CurrentGameInfo['mapId']]+" | "+QUEUE_ID_TO_NAME[CurrentGameInfo['gameQueueConfigId']]+' | '+ format_seconds(CurrentGameInfo['gameLength']))

    # get users profile pic and display
    embedVar.set_author(name=username,icon_url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/"+str(profileIconId)+".png")
    participants = CurrentGameInfo['participants']

    # display members of blue and red teams by position and champion
    blue_team_users = [i['summonerId'] for i in participants if i['teamId'] == BLUE_TEAM_ID]
    blue_team_ranks = {}
    for i in blue_team_users:
        leagueEntryDTOs = lv4.get_ranked_leagues(i)
        if leagueEntryDTOs == -1:
            await ctx.send(f"Error accessing Riot Games API. Please try again later.")
            return
        else:
            # filter on gamequeue
            rank_str = ""
            if QUEUE_ID_TO_NAME[CurrentGameInfo['gameQueueConfigId']] == "5v5 Ranked Solo games":
                rank_str = [i['tier']+" "+i['rank'] for i in leagueEntryDTOs if i['queueType'] == "RANKED_SOLO_5x5"][0]
            else:
                rank_str = [i['tier']+" "+i['rank'] for i in leagueEntryDTOs if i['queueType'] == "RANKED_FLEX_SR"][0]
            blue_team_ranks[i] = rank_str

    red_team_users = [i['summonerId'] for i in participants if i['teamId'] == RED_TEAM_ID]
    red_team_ranks = {}
    for i in red_team_users:
        leagueEntryDTOs = lv4.get_ranked_leagues(i)
        if leagueEntryDTOs == -1:
            await ctx.send(f"Error accessing Riot Games API. Please try again later.")
            return
        else:
            # filter on gamequeue
            rank_str = ""
            if QUEUE_ID_TO_NAME[CurrentGameInfo['gameQueueConfigId']] == "5v5 Ranked Solo games":
                rank_str = [i['tier']+" "+i['rank'] for i in leagueEntryDTOs if i['queueType'] == "RANKED_SOLO_5x5"][0]
            else:
                rank_str = [i['tier']+" "+i['rank'] for i in leagueEntryDTOs if i['queueType'] == "RANKED_FLEX_SR"][0]
            red_team_ranks[i] = rank_str



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
    embedVar.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/champion/"+CHAMPION_ID_TO_NAME[championId]+".png")
    await ctx.send(embed=embedVar)

@slash.slash(name="mastery",
             description="View a player's mastery score for a specific champion.",
             options=[
               create_option(name="username",description="Summoner Name",option_type=3,required=True),
               create_option(name="champion",description="Name of the champion",option_type=3,required=True)],guild_ids=guild_ids)
async def mastery(ctx, username:str,champion:str):
    encryptedSummonerID = sv4.username_to_encryptedSummonerID(username)
    profileIconId = sv4.username_to_profileIconId(username)

    # check for successful GET on encryptedSummonerID
    if encryptedSummonerID == -1 or profileIconId == -1:
        await ctx.send(f"The username "+username+" could not be found.")
        return
    username = sv4.username_to_username(username)
    #check champion input
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        await ctx.send(f"" + champion +" is not a valid champion name.")
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]
    mastery_dto = cm4.get_individual_championHistory(encryptedSummonerID,CHAMPION_NAME_TO_ID[champion.lower()])
    if mastery_dto == -1:
        await ctx.send(f""+username+" has no available mastery data for "+champion)
        return


    embedVar = discord.Embed(color=0x9932CC)

    # double dictionary lookup to ensure URL has upper/lowercasing consistent with riots api, regardless of user input
    embedVar.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/champion/"+champion+".png")
    embedVar.set_author(name=username,icon_url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/"+str(profileIconId)+".png")
    embedVar.add_field(name=champion,value=str(mastery_dto['championPoints'])+" points",inline=False)

    # convert from ms to s
    embedVar.add_field(name="Last Played",value=str(datetime.utcfromtimestamp(mastery_dto['lastPlayTime']/1000)),inline=True)

    # display png of mastery at bototm
    file = discord.File("images/mastery-"+str(mastery_dto['championLevel'])+".png",filename="mastery-"+str(mastery_dto['championLevel'])+".png")
    embedVar.set_image(url="attachment://mastery-"+str(mastery_dto['championLevel'])+".png")
    await ctx.send(embed=embedVar,file=file)

@slash.slash(name="championstats",
             description="View a user's KD/A, win rate, damage and other stats on a specific champion.",
             options=[
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
               ],guild_ids=guild_ids)
async def championstats(ctx,username:str,champion:str,queueId:int):
    encryptedAccountID = sv4.username_to_encryptedAccountID(username)
    profileIconId = sv4.username_to_profileIconId(username)
    if encryptedAccountID == -1 or profileIconId == -1:
        await ctx.send(f"The username "+username+" could not be found.")
        return
    username = sv4.username_to_username(username)
    #check champion input
    if champion.lower() not in CHAMPION_NAME_TO_ID:
        await ctx.send(f"" + champion +" is not a valid champion name.")
        return

    champion = CHAMPION_ID_TO_NAME[CHAMPION_NAME_TO_ID[champion.lower()]]


    embed = discord.Embed(color=0x9932CC,title="Fetching newest data...")
    embed.set_image(url="https://media.tenor.com/images/2629d421692a139c37b6c43492219a45/tenor.gif")

    message = await ctx.send(embed=embed)
    rdf = get_matches_from_db(encryptedAccountID,champion,username,queueId)
    df = rdf.groupby(['championName']).mean()

    queueName = None
    if queueId != 0:
        queueName = QUEUE_ID_TO_NAME[queueId]
    else:
        queueName = "All queues"

    embedVar = discord.Embed(color=0x9932CC,title=queueName+" stats on "+champion)
    # double dictionary lookup to ensure URL has upper/lowercasing consistent with riots api, regardless of user input
    embedVar.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/champion/"+champion+".png")
    embedVar.set_author(name=username,icon_url="http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/"+str(profileIconId)+".png")

    embedVar.add_field(name='Kills',value="{:.2f}".format(df['kills'][0]),inline=True)
    embedVar.add_field(name='Deaths',value="{:.2f}".format(df['deaths'][0]),inline=True)
    embedVar.add_field(name='Assists',value="{:.2f}".format(df['assists'][0]),inline=True)

    embedVar.add_field(name='K/DA',value=kda(df['kills'][0],df['deaths'][0],df['assists'][0]),inline=True)
    embedVar.add_field(name='Winrate',value="{:.2f}".format(df['win'][0]),inline=True)
    numWins = sum(rdf['win'])
    embedVar.add_field(name='Games played',value=str(len(rdf)) + " ("+str(numWins)+"W "+str(len(rdf)-numWins)+"L)",inline=True)

    embedVar.add_field(name='Total CS',value="{:.2f}".format(df['CS'][0]),inline=True)
    embedVar.add_field(name='CS/min',value="{:.2f}".format(df['CS/min'][0]),inline=True)
    embedVar.add_field(name='Gold Earned',value="{:.2f}".format(df['goldEarned'][0]),inline=True)

    embedVar.add_field(name='Champion Damage ',value="{:.2f}".format(df['totalDamageDealtToChampions'][0]),inline=True)
    embedVar.add_field(name='Damage Taken',value="{:.2f}".format(df['totalDamageTaken'][0]),inline=True)
    embedVar.add_field(name='First Blood %',value="{:.2f}".format(df['firstBlood'][0] * 100),inline=True)


    await message.edit(content="",embed=embedVar)



def get_matches_from_db(encryptedAccountID,champion,username,queueId=0):
    # Generate unix timestamp for 01/01/Current Year (LoL season start apprx.)
    year = datetime.date.today().year
    date = datetime.datetime(year, 1, 1)
    NEW_YEAR_TIME_STAMP = date.timestamp()

    # if user provided champion parameters, convert string to numeric id
    championId = CHAMPION_NAME_TO_ID[champion.lower()]

    # request accountId and check for valid response
    accountId = encryptedAccountID
    total = 0
    beginIndex= 0
    endIndex=100
    objects = []

    # find timestamp for most recent game stored in db. Only request riot api for
    # games that occured after this timestamp
    mostRecentGame =  db.matches.find({'accountId':encryptedAccountID}).sort("timestamp",-1)
    mostRecentTimestamp = None
    if db.matches.count_documents({'accountId':accountId}) != 0:
        mostRecentTimestamp = mostRecentGame[0]['timestamp']

    loop = True
    while loop:
        #get match list for 100 game window (max allowed by riot api) and check for valid response
        d = mv4.get_match_list(accountId,beginIndex=beginIndex,endIndex=endIndex)
        #check if d == -1
        if d == -1:
            # DISCORD MESSAGE HERE
            print("Could not retrieve match data for "+username)
            return -1


        #get list of matchDtos from api response d
        matchList = d['matches']
        for i in matchList:
            # MAKE REQUEST GETMATCH and check for valid response
            match = mv4.get_match(i['gameId'])
            if match == -1:
                if len(objects) > 0:
                    loop = False
                    break
                else:
                    return -1


            # only process matches in current season (year)
            if match['gameCreation']/1000 <= NEW_YEAR_TIME_STAMP: #conversion from ms to s
                loop = False
                break

            #exclude remake case (disconnected game less than 240 seconds)
            if match['gameDuration'] < 240:
                continue

            # only request matches from riot api for matches not in db
            if mostRecentTimestamp != None and match['gameCreation'] <= mostRecentTimestamp:
                loop = False
                break
            else:
                #find participantId for username- participantId is used to identify a user's game stats
                numPlayers = 10
                participantInfo = match['participantIdentities']
                participantId = 0
                for j in participantInfo:
                    if j['player']['accountId'] == accountId:
                        participantId = j['participantId']

                # riot uses 1 based indexing for array of participantstats
                participantStats = match['participants'][participantId-1]['stats']
                d = {
                    "accountId":accountId,
                    "username":username,
                    "gameId":match['gameId'],
                    "queueId":match['queueId'],
                    "championId":match['participants'][participantId-1]['championId'],
                    "championName":CHAMPION_ID_TO_NAME[match['participants'][participantId-1]['championId']],
                    "lane":match['participants'][participantId-1]['timeline']['lane'],
                    "role":match['participants'][participantId-1]['timeline']['role'],
                    "timestamp":match['gameCreation'],
                    "CS":participantStats['totalMinionsKilled']+participantStats['neutralMinionsKilled'],
                    "CS/min":(participantStats['totalMinionsKilled']+participantStats['neutralMinionsKilled'] )/(match['gameDuration']/60),
                    "kills":participantStats['kills'],
                    "deaths":participantStats['deaths'],
                    "assists":participantStats['assists'],
                    "goldEarned":participantStats['goldEarned'],
                    "totalDamageDealtToChampions":participantStats['totalDamageDealtToChampions'],
                    "damageDealtToObjectives":participantStats['damageDealtToObjectives'],
                    "totalDamageTaken":participantStats['totalDamageTaken'],
                    "firstBlood":participantStats['firstBloodKill'],
                    "firstBloodAssist":participantStats['firstBloodAssist'],
                    "win":participantStats['win']
                }
                objects.append(d)

        beginIndex += 100
        endIndex += 100

    if len(objects)>0:
        db.matches.insert_many(objects)

    # apply filters at the bitter end!
    df = pd.DataFrame(list(db.matches.find({'accountId':accountId,'championId':championId})))
    if queueId != 0:
        df = df[df['queueId']==queueId]
    return df

def format_seconds(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return "%02d:%02d" % (minutes,seconds)

def kda(kills,deaths,assists):
    if deaths == 0:
        return 'Perfect K/DA'
    else:
        return "{:.2f}".format((kills+assists)/deaths)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
client.run(BOT_TOKEN)
