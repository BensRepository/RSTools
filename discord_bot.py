import os
import django
import discord
from discord.ext import commands, tasks
import requests 
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup 
from asgiref.sync import sync_to_async  # 
from io import BytesIO
import feedparser
import datetime
from datetime import timedelta, time

import pytz
import random
import json
import asyncio
from WebApp.settings import STATIC_URL
# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WebApp.settings")
django.setup()

from playground.models import RSLeaderboardEntry
from playground.models import Weeklys
from playground.models import PollResults
# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def ping(ctx):
    """Test command."""
    await ctx.send("Pong!")

# ✅ mark ORM call as sync_to_async
@sync_to_async
def get_leaderboard_data():
    results = []
    objs = RSLeaderboardEntry.objects.filter(event="current")
    for obj in objs:
        results.append([
            obj.rsn,
            (obj.weeklybosskillscurrent - obj.weeklybosskillsstart),
            (obj.weeklyskillxpcurrent - obj.weeklyskillxpstart),
            (obj.totalxpcurrent - obj.totalxpstart),
        ])
    return results
@sync_to_async
def get_leaderboard_data_previous():
    results_previous = []
    objs_previous = RSLeaderboardEntry.objects.filter(event="previous")
    for obj in objs_previous:
        results_previous.append([
            obj.rsn,
            (obj.weeklybosskillscurrent - obj.weeklybosskillsstart),
            (obj.weeklyskillxpcurrent - obj.weeklyskillxpstart),
            (obj.totalxpcurrent - obj.totalxpstart),
        ])
    return results_previous
from discord import Embed
BOSS_WINNER_PHRASES = [
    "Stop bullying the bosses 😩",
    "Literally camping GWD 💀",
    "That's a LOT of boss kills... 🔥",
    "Someone's farming pets 🐉",
    "Bosses fear this one 😱",
]

SKILL_WINNER_PHRASES = [
    "Can this guy stop skilling? 📚",
    "Maxed? Again? 🧠",
    "Sweaty skiller energy 💦",
    "Just one more herb run... 🌿",
    "No XP waste detected 🛠️",
]

TOTAL_XP_WINNER_PHRASES = [
    "XP machine confirmed 🤖",
    "This guy is the economy 📈",
    "Stacking XP like a hoarder 💰",
    "A true grinder 🪓📚",
    "Can't stop, won't stop 🏃",
]
async def send_leaderboard(channel):
    try:
        results = await get_leaderboard_data()
        print("Created results")
    except Exception as e:
        print(e)
        await channel.send("⚠️ Failed to get leaderboard data")
        return

    try:
        weekly = await sync_to_async(lambda: Weeklys.objects.get(id=1))()

        boss_of_the_week = weekly.boss
        skill_of_the_week = weekly.skill
    except Weeklys.DoesNotExist:
        boss_of_the_week = "N/A"
        skill_of_the_week = "N/A"

    # Sort results
    sorted_data_boss = sorted(results, key=lambda x: x[1], reverse=True)[:9]
    sorted_data_skill = sorted(results, key=lambda x: x[2], reverse=True)[:9]
    sorted_data_total_xp = sorted(results, key=lambda x: x[3], reverse=True)[:9]

    # Random winner messages
    boss_phrase = random.choice(BOSS_WINNER_PHRASES)
    skill_phrase = random.choice(SKILL_WINNER_PHRASES)
    total_xp_phrase = random.choice(TOTAL_XP_WINNER_PHRASES)

    # Calculate time remaining until Sunday midnight
    now = datetime.datetime.now(pytz.utc)  # use timezone-aware datetime
    # Find next Sunday midnight
    days_ahead = 6 - now.weekday()  # weekday(): Monday=0 ... Sunday=6
    if days_ahead < 0:
        days_ahead += 7
    next_sunday_midnight = (now + datetime.timedelta(days=days_ahead)).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(days=1)  # midnight at the *end* of Sunday
    time_remaining = next_sunday_midnight - now

    # Format nicely (e.g., "2 days, 5h 32m")
    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    time_remaining_str = f"{days}d {hours}h {minutes}m"

    # Build embed
    embed = discord.Embed(title="🏆 RSTools Weekly Leaderboard", color=0x00ff00)

    embed.add_field(
        name=f"⚔️ Boss of the Week: {boss_of_the_week}\n🥇 {sorted_data_boss[0][0]} - {boss_phrase}",
        value="\n".join(f"{r[0]}: {r[1]:,} KC" for r in sorted_data_boss),
        inline=False
    )

    embed.add_field(
        name=f"🌳 Skill of the Week: {skill_of_the_week}\n🥇 {sorted_data_skill[0][0]} - {skill_phrase}",
        value="\n".join(f"{r[0]}: {r[2]:,} XP" for r in sorted_data_skill),
        inline=False
    )

    embed.add_field(
        name=f"📊 Total XP Leaderboard\n🥇 {sorted_data_total_xp[0][0]} - {total_xp_phrase}",
        value="\n".join(f"{r[0]}: {r[3]:,} XP" for r in sorted_data_total_xp),
        inline=False
    )

    embed.set_footer(text=f"⏳ Time remaining: {time_remaining_str}")

    await channel.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    """Returns current weekly leaderboard results"""
    await send_leaderboard(ctx.channel)

@tasks.loop(minutes=1)  # check every minute
async def weekly_leaderboard_task():
    now = datetime.datetime.now(tz=london_tz)
    if now.weekday() == 2 and now.hour == 16 and now.minute == 0:  # Wednesday is 2 (Mon=0)
        channel = bot.get_channel(1293597750134444156)  # Replace with your channel ID
        if channel:
            await channel.send("📊 Here are your current standings — halfway through the week! Keep grinding and good luck to everyone! 💪🔥")
            await send_leaderboard(channel)
        else:
            print("⚠️ Weekly leaderboard task: Channel not found.")






# Joke command
jokes = [
"I saw someone killing red spiders a few years ago and reported him for bug abuse.",
"Your momma's so fat she's got enough chins for 99 range.",
"Instead of water boarding, the US government should make the terrorists catch hell rats with a kitten.",
"Yo momma so fat a dhally spec hits her three times.",
"Ur mum is like the Al Kharid gate, only 10 gp to enter.",
"Eyy gurl, are u 99 Farming because ur making me grow.",
"What do you call somebody with 99 fishing? A Master Baiter.",
"Yo' momma's so fat that it takes 10 nature runes to alch her.",
"Yo momma so fat she takes up her own inventory spaces.",
"Aye bb, you get 99 herblore? Cause you took all my money.",
"Yo momma's so fat, Ice Barrage can't stop her!",
"Zezima went up to a drug dealer and asked 'Herblore level?'",
"Zezima went to McDonalds and asked 'Cooking levels?",
"Zezima saw fireworks and asked someone 'Who Leveld?",
"How do you stop 9/11? Drink a super restore",
"You know you're addicted to runescape when your girlfriend's pants have a low drop rate.",
"How many OSRS players does it take to screw in a lightbulb? 99, 7 to screw in the lightbulb and the other half to complain about how the lightbulb was better in 2007.",
"What is my OSRS gf's favorite job? Ahrim job.",
"Your mom is so fat that she activated sand crabs when she started tutorial island.",
"What’s Soulja Boy's favourite tree? YEWWWWWWWWWW.",
"What do you call head from a grandma? Ancestral top.",
"Girl, call me the RuneScape servers because I’m crashing at your place tonight.",
"Jagex support.",
"Yo momma’s so fat she still gets hit hiding behind pillars at inferno.",
"Yo momma’s so fat she eats at full health.",
"Yo mama so fat when she spawned in Lumbridge she unlocked all the music tracks.",
"Buried your mom. Got 99 prayer.",
"Do you have 20 runecrafting, because you can enter my body altar ",
"Maxed Firemaking? That's pretty hot.",
"Instead of water boarding, the US government should make the terrorists catch hell rats with a kitten.",
"Two Mushroom men were walking down the road, one of them Australian. The Australian one suddenly stops and says 'That's as far Zygomite.'",
"Maxed Woodcutting? I Wood totally hang out with Yew.",
"Do you have 40 prayer? You’re gonna need some protection from my missle👀",
"I have killed Graardor, Zilyana, K'ril and Kree, who comes Nex?",
"Despite popular beliefs nobody that plays Runescape is a virgin, we have all been fucked by Jagex at least once.",
"Oh, you made your first 10k selling bowstrings? Weird flax, but okay.",
"She showed me her ba-bas so I hit it from zebak.",
"What do you call a F2P with 99 Magic? An alch-oholic.",
"Knock knock - Whos there? - Reported for asking for personal information",
"Did you hear about the mage that tried to steal a television set? He was caught casting Telly-Grab."
]
@bot.command()
async def joke(ctx):
    """Tells a 11/10 OSRS Joke."""

    await ctx.send(random.choice(jokes))


london_tz = pytz.timezone("Europe/London")

# @tasks.loop(time=datetime.time(hour=12, minute=30, tzinfo=london_tz))
# async def daily_joke():
#     channel = bot.get_channel(1293597750134444156)
#     if channel:
#         await channel.send("😂 **Here’s your daily OSRS joke!** 😂")
#         await channel.send(random.choice(jokes))
#     else:
#         print("⚠️ Channel not found")

import difflib


# --- OSRS Skills & Emojis (your list) ---
SKILLS = {
    "Overall": "📊",
    "Attack": "🗡️",
    "Defence": "🛡️",
    "Strength": "✊",
    "Hitpoints": "❤️",
    "Ranged": "🏹",
    "Prayer": "🌟",
    "Magic": "🧙",
    "Cooking": "🍲",
    "Woodcutting": "🌳",
    "Fletching": "🔄",
    "Fishing": "🎣",
    "Firemaking": "🔥",
    "Crafting": "⚒️",
    "Smithing": "🔨",
    "Mining": "⛏️",
    "Herblore": "🌿",
    "Agility": "🏃",
    "Thieving": "💰",
    "Slayer": "💀",
    "Farming": "👨‍🌾",
    "Runecrafting": "💫",  
    "Hunter": "🐾",
    "Construction": "🏠",
}


BOSS_EMOJIS = {
    "Clue Scrolls (all)": "🗺️",
    "Clue Scrolls (beginner)": "📜",
    "Clue Scrolls (easy)": "📜",
    "Clue Scrolls (medium)": "📜",
    "Clue Scrolls (hard)": "📜",
    "Clue Scrolls (elite)": "📜",
    "Clue Scrolls (master)": "📜",

    "Rifts closed": "🌌",
    "Collections Logged": "📚",

    "Abyssal Sire": "🦑",
    "Alchemical Hydra": "🐍",
    "Amoxliatl": "🦂",
    "Araxxor": "🕷️",
    "Artio": "🐻",
    "Barrows Chests": "⚰️",
    "Bryophyta": "🌿",
    "Callisto": "🦁",
    "Calvar'ion": "🐺",
    "Cerberus": "🐶",
    "Chambers of Xeric": "🏛️",
    "Chambers of Xeric Challenge Mode": "🏛️",
    "Chaos Elemental": "🌪️",
    "Chaos Fanatic": "🤪",
    "Commander Zilyana": "🕊️",
    "Corporeal Beast": "👹",
    "Crazy Archaeologist": "📖",
    "Dagannoth Prime": "👑",
    "Dagannoth Rex": "🦖",
    "Dagannoth Supreme": "⚔️",
    "Deranged Archaeologist": "📖",
    "Doom of Mokhaiotl": "☠️",
    "Duke Sucellus": "💀",
    "General Graardor": "🪖",
    "Giant Mole": "🐹",
    "Grotesque Guardians": "🪦",
    "Hespori": "🌱",
    "Kalphite Queen": "🐜",
    "King Black Dragon": "🐉",
    "Kraken": "🐙",
    "Kree'Arra": "🦅",
    "K'ril Tsutsaroth": "😈",
    "Lunar Chests": "🌙",
    "Mimic": "🎭",
    "Nex": "❄️",
    "Nightmare": "🌌",
    "Phosani's Nightmare": "🌌",
    "Obor": "🪨",
    "Phantom Muspah": "👻",
    "Sarachnis": "🕷️",
    "Scorpia": "🦂",
    "Scurrius": "🐀",
    "Skotizo": "🪬",
    "Sol Heredit": "☀️",
    "Spindel": "🕸️",
    "Tempoross": "🌊",
    "The Gauntlet": "🏹",
    "The Corrupted Gauntlet": "🏹",
    "The Hueycoatl": "🐍",
    "The Leviathan": "🐊",
    "The Royal Titans": "👑",
    "The Whisperer": "🫢",
    "Theatre of Blood": "🩸",
    "Theatre of Blood Hard Mode": "🩸",
    "Thermonuclear Smoke Devil": "💨",
    "Tombs of Amascut": "🏺",
    "Tombs of Amascut Expert Mode": "🏺",
    "TzKal-Zuk": "🔥",
    "TzTok-Jad": "🔥",
    "Vardorvis": "⚔️",
    "Venenatis": "🕷️",
    "Vet'ion": "🪦",
    "Vorkath": "🐲",
    "Wintertodt": "❄️",
    "Yama": "👹",
    "Zalcano": "⛰️",
    "Zulrah": "🐍"
}
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO



def fetch_osrs_stats(username: str):
    """Fetch OSRS skill levels from official hiscores."""
    url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={username}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    lines = resp.text.strip().split("\n")
    return [int(line.split(",")[1]) for line in lines[:len(SKILLS)]]

@bot.command()
async def stats(ctx, *, username: str):
    """Fetch OSRS stats and display them vertically with perfect alignment."""
    await ctx.send(f"📊 Fetching stats for **{username}**...")

    levels = fetch_osrs_stats(username)
    if not levels:
        await ctx.send(f"❌ Could not fetch stats for **{username}**.")
        return

    lines = []
    for (skill, emoji), level in zip(SKILLS.items(), levels):
        # emoji separate; skill name padded to 14, level right-aligned to 4
        lines.append(f"{emoji}  {skill:<14}: {level:>4}")

    table_output = "```\n" + "\n".join(lines) + "\n```"
    STAT_PHRASES = [
        "What a noob... 📈",
        "Maxed when? 🧙",
        "Get those gains! 💪",
        "Training AFK again, huh? 💤",
        "You call *that* a total level? 😂",
        "No XP waste! 🏃‍♂️",
        "Statistically... mid. 📊",
        "Sweaty skiller detected! 🧂",
        "Click more rocks. ⛏",
        "Probably botted. 🤖",
        "Time to touch grass 🌱",
    ]
    embed = discord.Embed(
    title=f"{username}'s OSRS Stats",
    description=random.choice(STAT_PHRASES),  # 👈 Randomized message
    color=0x2ecc71
)


    await ctx.send(embed=embed)
    await ctx.send(table_output)



    # Combine both columns with fixed spacing (40 chars





last_posted = None  # Keep track of latest news link


def fetch_osrs_news():
    feed_url = "https://secure.runescape.com/m=news/latest_news.rss?oldschool=1"
    feed = feedparser.parse(feed_url)

    news_items = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        summary_html = entry.summary

        soup = BeautifulSoup(summary_html, "html.parser")
        summary_text = soup.get_text(strip=True)

        news_items.append((title, link, summary_text))

    return news_items


@bot.command()
async def news(ctx, count: int = 1):
    """Manually fetch latest OSRS news and post in Discord."""
    news_items = fetch_osrs_news()
    if not news_items:
        await ctx.send("Could not fetch OSRS news right now.")
        return

    for title, link, summary in news_items[:count]:
        embed = discord.Embed(
            title=title,
            url=link,
            description=summary,
            color=0x00ff00
        )
        await ctx.send(embed=embed)


@tasks.loop(minutes=60)  # check every 5 minutes
async def check_news():
    global last_posted
    channel = bot.get_channel(1293597750134444156)  # replace with your channel ID

    news_items = fetch_osrs_news()
    if not news_items:
        return

    latest_title, latest_link, summary = news_items[0]

    # If this is the first run, just store it without posting
    if last_posted is None:
        last_posted = latest_link
        return

    # If there's a new post
    if latest_link != last_posted:
        last_posted = latest_link

        # Send a friendly notification message
        await channel.send("📢 **New Old School RuneScape news post!** 🎉 Check it out below:")

        embed = discord.Embed(
            title=latest_title,
            url=latest_link,
            description=summary,
            color=0x00ff00
        )
        await channel.send(embed=embed)


# @bot.event
# async def on_ready():
#     print(f"Logged in as {bot.user}")
#     check_news.start()  # start the background loop
#     global channel
#     channel = bot.get_channel(1293597750134444156)
#     if not daily_joke.is_running():
#         daily_joke.start()
minigameNames = [
 "Clue Scrolls (all)", "Clue Scrolls (beginner)",
    "Clue Scrolls (easy)", "Clue Scrolls (medium)", "Clue Scrolls (hard)", "Clue Scrolls (elite)",
    "Clue Scrolls (master)",
    "Rifts closed", "Collections Logged", "Abyssal Sire", "Alchemical Hydra",
    "Amoxliatl", "Araxxor", "Artio", "Barrows Chests", "Bryophyta", "Callisto", "Calvar'ion",
    "Cerberus", "Chambers of Xeric", "Chambers of Xeric Challenge Mode", "Chaos Elemental",
    "Chaos Fanatic", "Commander Zilyana", "Corporeal Beast", "Crazy Archaeologist",
    "Dagannoth Prime", "Dagannoth Rex", "Dagannoth Supreme", "Deranged Archaeologist",
    "Doom of Mokhaiotl", "Duke Sucellus", "General Graardor", "Giant Mole",
    "Grotesque Guardians", "Hespori", "Kalphite Queen", "King Black Dragon", "Kraken", "Kree'Arra",
    "K'ril Tsutsaroth", "Lunar Chests", "Mimic", "Nex", "Nightmare", "Phosani's Nightmare",
    "Obor", "Phantom Muspah", "Sarachnis", "Scorpia", "Scurrius", "Skotizo", "Sol Heredit",
    "Spindel", "Tempoross", "The Gauntlet", "The Corrupted Gauntlet", "The Hueycoatl",
    "The Leviathan", "The Royal Titans", "The Whisperer", "Theatre of Blood",
    "Theatre of Blood Hard Mode", "Thermonuclear Smoke Devil", "Tombs of Amascut",
    "Tombs of Amascut Expert Mode", "TzKal-Zuk", "TzTok-Jad", "Vardorvis", "Venenatis",
    "Vet'ion", "Vorkath", "Wintertodt", "Yama", "Zalcano", "Zulrah"
]
CHANNEL_ID = 1293597750134444156
# --- Boss Emojis Mapping ---


# --- Poll Data (updated) ---


emojisSkills = [
    "🗡️", "🛡️", "✊", "❤️", "🏹", "🌟", "🧙", "🍲", "🌳",
    "🔄", "🎣", "🔥", "⚒️", "🔨", "⛏️", "🌿", "🏃", "💰", "💀",
    "👨‍🌾", "💫", "🐾", "🏠"
]
poll_data = {
    "Boss of the week": {"message": None, "options": [], "emojis": []},  # we'll assign dynamically
    "Skill of the week": {"message": None, "options": [], "emojis": emojisSkills},
}
SKILLNAMES = [
    "Attack",
    "Defence",
    "Strength",
    "Hitpoints",
    "Ranged",
    "Prayer",
    "Magic",
    "Cooking",
    "Woodcutting",
    "Fletching",
    "Fishing",
    "Firemaking",
    "Crafting",
    "Smithing",
    "Mining",
    "Herblore",
    "Agility",
    "Thieving",
    "Slayer",
    "Farming",
    "Runecrafting",
    "Hunter",
    "Construction",
]

@tasks.loop(minutes=1)
async def boss_poll_scheduler():
    await run_poll(minigameNames, "Boss of the week")

@tasks.loop(minutes=1) ##change to 24 hours and above
async def skill_poll_scheduler():
    await run_poll(SKILLNAMES, "Skill of the week")
poll_data = {
    "Boss of the week": {"message": None, "options": [],"emojis":BOSS_EMOJIS},
    "Skill of the week": {"message": None, "options": [],"emojis":emojisSkills},
}
async def run_poll(data, poll_type):
    now = datetime.datetime.now()
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return


    if now.weekday() == 5 and now.hour == 20 and now.minute == 30:
        options = random.sample(data, 5)

        if poll_type == "Skill of the week":
            description = "\n".join(f"{SKILLS[opt]} {opt}" for opt in options)
            message = await channel.send(
                f"📊 **Next {poll_type}!**\n\n{description}\n\n⏳ Poll closes Sunday 5PM!"
            )
            for opt in options:
                await message.add_reaction(SKILLS[opt])

        else:  # Boss of the week
            description = "\n".join(f"{BOSS_EMOJIS[opt]} {opt}" for opt in options)
            message = await channel.send(
                f"📊 **Next {poll_type}!**\n\n{description}\n\n⏳ Poll closes Sunday 5PM!"
            )
            for opt in options:
                await message.add_reaction(BOSS_EMOJIS[opt])

        poll_data[poll_type]["message"] = message
        poll_data[poll_type]["options"] = options


    message = poll_data[poll_type]["message"]
    options = poll_data[poll_type]["options"]

    if message is not None and now.weekday() == 6 and now.hour == 20 and now.minute == 30:
        message = await channel.fetch_message(message.id)

        results = []
        if poll_type == "Skill of the week":
            for opt in options:
                emoji = SKILLS[opt]
                reaction = discord.utils.get(message.reactions, emoji=emoji)
                votes = (reaction.count - 1) if reaction else 0
                results.append((opt, votes))
        else:
            for opt in options:
                emoji = BOSS_EMOJIS[opt]
                reaction = discord.utils.get(message.reactions, emoji=emoji)
                votes = (reaction.count - 1) if reaction else 0
                results.append((opt, votes))

        results.sort(key=lambda x: x[1], reverse=True)
        winner, win_votes = results[0]

        votedOption = await sync_to_async(PollResults.objects.get)(id=1)
        if poll_type == "Skill of the week":
            votedOption.skill = winner
        else:
            votedOption.boss = winner
        await sync_to_async(votedOption.save)(update_fields=['boss','skill'])

        results_text = "\n".join(
            f"{(SKILLS.get(opt) if poll_type == 'Skill of the week' else BOSS_EMOJIS.get(opt))} **{opt}** — {v} vote(s)"
            for opt, v in results
        )
        await message.channel.send(
            f"📊 **Poll Results:**\n\n{results_text}\n\n🏆 **Winner:** {winner} with {win_votes} vote(s)!"
        )

        poll_data[poll_type]["message"] = None
        poll_data[poll_type]["options"] = []


@tasks.loop(minutes=1)
async def monday_winners_task():
    now = datetime.datetime.now(tz=london_tz)
    if now.weekday() == 0 and now.hour == 12 and now.minute == 0:# Monday at 12:00
        channel = bot.get_channel(1293597750134444156)  # Replace with your channel ID
        if channel:
            # Get the latest weekly info
            try:
                weekly = await sync_to_async(lambda: Weeklys.objects.get(id=1))()
                skill_of_the_week = weekly.skill
                boss_of_the_week = weekly.boss
            except Weeklys.DoesNotExist:
                skill_of_the_week = "N/A"
                boss_of_the_week = "N/A"
            results_previous = await get_leaderboard_data_previous()
            sorted_data_boss = sorted(results_previous, key=lambda x: x[1], reverse=True)[:9]
            sorted_data_skill = sorted(results_previous, key=lambda x: x[2], reverse=True)[:9]
            sorted_data_total_xp = sorted(results_previous, key=lambda x: x[3], reverse=True)[:9]
            message = (
                f"🏆 Last weeks's results! Winner winner chicken dinner! 🍗🎉\n\n"
                f"🏆 --Bossing Champion - **{sorted_data_boss[0][0]}**, --Skilling God **{sorted_data_skill[0][0]}**, --XP King **{sorted_data_total_xp[0][0]}**\n"
                f"🔮 **NEW Skill of the Week:** {SKILLS.get(skill_of_the_week, '')} {skill_of_the_week}\n"
                f"👹 **NEW Boss of the Week:** {BOSS_EMOJIS.get(boss_of_the_week, '')} {boss_of_the_week}\n"
                f"🎯 **Good Luck!**"
            )

            await channel.send(message)

        else:
            print("⚠️ Monday winners task: Channel not found.")
import aiohttp
import urllib.parse
import re
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")



MEME_CHANNEL_ID = 1293597750134444156  # Replace this

# Meme folder path
base_dir = os.path.dirname(os.path.abspath(__file__))
MEME_FOLDER = os.path.join(base_dir, 'static', 'images', 'memes')

# File to track posted memes
POSTED_MEMES_FILE = os.path.join(base_dir, 'static', 'posted_memes.json')


def load_posted_memes():
    """Load already posted meme filenames."""
    if os.path.exists(POSTED_MEMES_FILE):
        with open(POSTED_MEMES_FILE, 'r') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()


def save_posted_memes(memes_set):
    """Save posted meme filenames."""
    with open(POSTED_MEMES_FILE, 'w') as f:
        json.dump(list(memes_set), f, indent=2)


@tasks.loop(minutes=1)
async def meme_post_task():
    now = datetime.datetime.now(tz=london_tz)

    # Monday=0, Wednesday=2, Friday=4 → 12:00 PM
    if now.weekday() in [0, 4] and now.hour == 12 and now.minute == 0:
        channel = bot.get_channel(MEME_CHANNEL_ID)
        if not channel:
            print("⚠️ Meme task: Channel not found.")
            return

        posted_memes = load_posted_memes()

        # All available memes
        memes = [
            f for f in os.listdir(MEME_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]

        # Filter out already posted memes
        available_memes = [m for m in memes if m not in posted_memes]

        if not available_memes:
            await channel.send("⚠️ All memes have been posted! Please add new ones 😅")
            print("⚠️ Meme folder exhausted.")
            return

        # Pick a random meme
        meme_choice = random.choice(available_memes)
        meme_path = os.path.join(MEME_FOLDER, meme_choice)

        # Day-specific message
        day_messages = {
            0: "😎 **Let's start the week with a meme! Work sucks... *",
            4: "🎉 **Weekend’s almost here — Meme Time!**"
        }

        # Default if weekday isn’t in dict (for safety)
        intro_message = day_messages.get(now.weekday(), "😂 **Meme Time!**")

        # Send meme
        file = discord.File(meme_path)
        await channel.send(intro_message, file=file)
        print(f"✅ Posted meme: {meme_choice}")

        # Record that it’s been posted
        posted_memes.add(meme_choice)
        save_posted_memes(posted_memes)
    else:
        pass  # Not the right time


@bot.command(name="meme")
async def meme(ctx):
    """Test command to post a meme immediately (ignores date/time)."""
    channel = ctx.channel
    posted_memes = load_posted_memes()

    memes = [
        f for f in os.listdir(MEME_FOLDER)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    ]


    meme_choice = random.choice(memes)
    meme_path = os.path.join(MEME_FOLDER, meme_choice)

    file = discord.File(meme_path)
    await channel.send("Meme Time!", file=file)

    # Optionally record it as posted to avoid duplicates

    save_posted_memes(posted_memes)

    print(f"meme sent: {meme_choice}")


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    if not weekly_leaderboard_task.is_running():
        weekly_leaderboard_task.start()
    if not monday_winners_task.is_running():   # <-- check its own status
        monday_winners_task.start()            # <-- no parentheses here!

    if not check_news.is_running():
        check_news.start()
    # --- Start scheduled loop for future runs ---
    # if not daily_joke.is_running():
    #     daily_joke.start()
    if not boss_poll_scheduler.is_running():
        boss_poll_scheduler.start()

    if not skill_poll_scheduler.is_running():
        skill_poll_scheduler.start()

    if not meme_post_task.is_running():
        meme_post_task.start()
TOKEN = ""
bot.run(TOKEN)