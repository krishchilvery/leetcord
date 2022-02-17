from dis import disco
import re
from tokenize import group
from turtle import color
import discord
import os
import logging

from matplotlib.pyplot import title

from leetcode_client import LeetcodeClient

client = discord.Client()
token = os.getenv("LeetcordToken")

lc = LeetcodeClient()

@client.event
async def on_ready():
    print("Connection established to Discord Servers")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('<>'):
       await process_bot_commands(message)
        

async def process_bot_commands(message):
    command = message.content[2:].strip().lower()
    if command == "hello":
        await message.channel.send('Leetcord at your service!')
    if command == "problem":
        await message.channel.send('Question coming right')
        qem = c_problem(command)
        await message.channel.send(embed=qem)

def c_problem(command: str) -> discord.Embed:
    dif_regex = re.compile(r"^(?i)(easy|medium|hard|e|m|h|\*+)$")
    match = dif_regex.match(command)
    if match:
        dif = match.group(0).lower()
        if dif == "easy" or dif == "e" or dif == "*":
            dif = "Easy"
        elif dif == "medium" or dif == "m" or dif == "**":
            dif = "Medium"
        elif dif == "hard" or dif == "h" or dif == "***":
            dif = "Hard"
        question = lc.get_random_question_with_difficulty(dif)
    else:
        question = lc.get_random_question()
    question_embed = discord.Embed(
        title=question.get("title", ""),
        description=f"Difficulty: {question.get('difficulty', 'Unknown')}",
        url=f"https://leetcode.com/problems/{question.get('slug', 'two-sum')}/",
        color=discord.Color.random()
    )
    return question_embed
        
client.run(token)