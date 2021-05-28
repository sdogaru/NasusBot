import discord
import os
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

intents = discord.Intents(messages=True, guilds=True)
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

enabled = True

"""
When the bot is added to a server, send a gif in chat to introduce
"""
@client.event
async def on_guild_join(guild):
    general = discord.utils.find(lambda x: x.name == 'general',  guild.text_channels)
    if general:
        await general.send(file=discord.File('ahri_gif.gif'))
        await general.send("Hi, I'm Ahri - a Discord bot for all things League of Legends! To get started, use the /help command.")

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
async def test(ctx,username: str):
    await ctx.send(f"Checking " + username, hidden=True)



load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
client.run(BOT_TOKEN)
