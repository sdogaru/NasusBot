import discord

client = discord.Client()
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

client.run("NzIyNzE2MzE3MTYwODMzMTE0.XunIIg.UxLdWCd8y73veXvZUHo9v0sve48")
