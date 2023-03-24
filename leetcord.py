import os

from leetcord_commands import bot

token = os.getenv("LeetcordToken")

bot.run(token)