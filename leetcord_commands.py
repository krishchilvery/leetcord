import re
import datetime as dt
import sched
from typing import Optional
from discord import Embed, Color, Intents
from discord.ext import commands, tasks

from leetcode_client import LeetcodeClient
from leetcord_api import LeetcordClient

DEFAULT_TIME = "10:30 AM"
DEFAULT_TIMEZONE = "GMT+0"
DEFAULT_YEAR = 2020
DEFAULT_MONTH = 1
DEFAULT_DAY = 1

bot = commands.Bot(command_prefix="<<")

lc = LeetcodeClient()
ac = LeetcordClient()

class Leetcord(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        ac.add_guild(str(guild.id), guild.name)
        try:
            await guild.system_channel.send("Leetcode here to serve!")
        except ValueError:
            pass
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        ac.delete_guild(str(guild.id))
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.start_riddler()

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.name}! Hope you are having a great day :smile:")

    @commands.command()
    async def problem(self, ctx, dif: Optional[str] = None):

        await ctx.send("Question coming right up!")
        
        # Format difficulty
        dif = dif.lower() if dif else None
        if dif == "easy" or dif == "e" or dif == "*":
            dif = "Easy"
        elif dif == "medium" or dif == "m" or dif == "**":
            dif = "Medium"
        elif dif == "hard" or dif == "h" or dif == "***":
            dif = "Hard"
        else:
            dif = None

        # Get question
        question = lc.get_random_question_with_difficulty(dif) if dif else lc.get_random_question()

        # Format question embed
        question_embed = format_question_embed(question)
        
        # Send response
        await ctx.send(embed=question_embed)

    @commands.command()
    async def subscribe(self, ctx, time: Optional[str] = None, timezone: Optional[str] = None):
        
        # Validate Inputs
        if time is None:
            time = DEFAULT_TIME
        if timezone is None:
            timezone = DEFAULT_TIMEZONE

        # Validate Time
        try:
            hour, min = validate_time(time)
        except ValidationError:
            await ctx.send("Incorrect time format. Please ensure `HH:[00|30][AM|PM]` format.")
            return

        # Validate Timezone
        try:
            sign, hd, md = validate_timezone(timezone)
        except ValidationError:
            await ctx.send("Incorrect timezone format. Please ensure `GMT[+|-]DD[00|30|]` format.")
            return
        
        # Calculate UTC Time
        try:
            hour, min = calculate_time(hour, min, hd, md, sign)
        except ValidationError:
            await ctx.send("Incorrect timezone format. Please ensure `GMT[+|-]DD[00|30|]` format.")
            return

        time_obj = dt.datetime(year=DEFAULT_YEAR, month=DEFAULT_MONTH, day=DEFAULT_DAY, hour=hour, minute=min)

        ac.add_channel(str(ctx.channel.id), ctx.channel.name, str(ctx.guild.id), time_obj)
        await ctx.send(f"Successfully registered channel #{ctx.channel.name} from Server <{ctx.guild.name}> to receive a question every day at {time} {timezone}")

    @commands.command()
    async def unsubscribe(self, ctx):
        ac.delete_channel(str(ctx.channel.id))
        await ctx.send(f"Sorry to see you go :cry:.{ctx.channel.name} unsubscribed")

    @tasks.loop(minutes=1)
    async def riddler(self):
        now = dt.datetime.utcnow()
        min = now.minute
        hour = now.hour
        if not (min == 0 or min == 30):
            return
        time = dt.datetime(
            year=DEFAULT_YEAR,
            month=DEFAULT_MONTH,
            day=DEFAULT_DAY,
            hour=hour,
            minute=min
        )
        question = lc.get_random_question()
        question_embed = format_question_embed(question)
        channels = ac.get_channels_with_time(time)
        for channel in channels:
            id = int(channel[0])
            ctx = self.bot.get_channel(id)
            try:
                await ctx.send("Aloha! Its time for some coding. :technologist:")
                await ctx.send("Here's your question of the day.")
                await ctx.send(embed=question_embed)
            except AttributeError:
                print(f"Channel <{id}> not found")
    
    def start_riddler(self):
        # import time
        # start_time = get_nearest_round_time()
        # s = sched.scheduler(time.time, time.sleep)
        # start = self.riddler.start
        # s.enterabs(start_time.timestamp(), 1, start)
        # s.run()
        self.riddler.start()

    def cog_unload(self):
        self.riddler.cancel()

def format_question_embed(question: dict) -> Embed:
    question_embed = Embed(
        title=question.get("title", ""),
        type="rich",
        description=f"Difficulty: **{question.get('difficulty', 'Unknown')}**",
        url=f"https://leetcode.com/problems/{question.get('slug', 'all')}/",
        color=Color.random()
    )
    return question_embed

def get_nearest_round_time():
    time = dt.datetime.utcnow()
    if 0 <= time.minute < 30:
        time = time.replace(second=0, microsecond=0, minute=30)
    elif 30 <= time.minute < 60:
        time = time.replace(second=0, microsecond=0, minute=0) + dt.timedelta(hours=1)
    time = time.replace(tzinfo=dt.timezone.utc)
    return time
        

def validate_time(time):
    time_regex = re.compile(r"^(\d\d?):(00|30)(AM|PM)?$", re.IGNORECASE)
    time = time.strip().upper()
    match = time_regex.match(time)
    if match is None:
        raise ValidationError
    hour = int(match.group(1))
    min = int(match.group(2))
    if match.group(3):
        if match.group(3) == "AM":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12
    if hour >= 24 or min >= 60:
        raise ValidationError
    return hour, min

def validate_timezone(timezone):
    timezone_regex = re.compile(r"^(GMT)?(\+|\-)(\d\d?)(00|30)?$", re.IGNORECASE)
    timezone = timezone.strip().upper()
    match = timezone_regex.match(timezone)
    if match is None:
        raise ValidationError
    sign = match.group(2)
    hour = int(match.group(3))
    if match.group(4):
        min = int(match.group(4))
    else:
        min = 0
    if hour > 12:
        raise ValidationError
    return sign, hour, min

def calculate_time(h, m, hd, md, sign):
    if sign == "-":
        m = m + md
        if m >= 60:
            m = m - 60
            h = (h + 1) % 24
        h = (h + hd) % 24
    elif sign == "+":
        m = m - md
        if m < 0:
            m = abs(m)
            h = (24 + h - 1) % 24
        h = (24 + h - hd) % 24
    else:
        raise ValidationError
    return h, m

class ValidationError(Exception):
    pass

bot.add_cog(Leetcord(bot))