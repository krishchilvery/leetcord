import discord
import os
import logging

logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)

client = discord.Client()
token = os.getenv("LeetcordToken")

@client.event
async def on_ready():
    logging.info("Connection established to Discord Servers")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('<>'):
        await message.channel.send('Welcome to Leetcord!')

def process_bot_commands(message):
    print(message)

client.run(token)