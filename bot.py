# bot.py
# import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.utils import get
import os
import io
import sys
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from pymongo import MongoClient
# from transformers import pipeline -- add text summary later

# env var handling of token and mongo connection
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URL = os.getenv("MONGO_URL")
cluster = MongoClient(MONGO_URL)

db = cluster["test"]

text_col = db["text"]

# https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be


# folders paths are in
initial_extensions = ['cogs.nlp']

bot = commands.Bot(command_prefix="^")

# Here we load our extensions(cogs) listed above in [initial_extensions].
# if __name__ == '__main__':
for extension in initial_extensions:
    print(extension)
    bot.load_extension(extension)
    cog = bot.get_cog('Nlp Commands')
    commands = cog.get_commands()
    print([c.name for c in commands])


@bot.command()
async def test(ctx):
    '''this is just a test'''
    await ctx.send("server metrics bot test")


@bot.command()
async def mongscrape(ctx):
    '''scrape all messages and dump content, time, author,
    sentiment polarity into mongodb atlas instance'''

    mongo_docs = []
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            blob = TextBlob(message.content)
            polarity = blob.sentiment.polarity
            mongo_docs.append({'content': message.content,
                               'time': message.created_at,
                               'author': message.author.name,
                               'polarity': polarity})
    text_col.insert_many(mongo_docs)
    await ctx.send("finished scraping to mongo")


@bot.command()
async def countreact(ctx):
    '''give a count of each emoji used in text channels
    (should refactor for just top emojis)'''

    counter = 0
    emojis = {}
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            for react in message.reactions:
                if not react.emoji in emojis:
                    emojis[react.emoji] = 1
                else:
                    emojis[react.emoji] += 1
    await ctx.send(emojis)


@bot.command()
async def sentiment(ctx):
    '''give the TextBlob polarity of a passed in string
    as positive, neutral or negative'''

    blob = TextBlob(ctx.message.content)
    polarity = blob.sentiment.polarity
    if polarity == 0:
        await ctx.send("That message seemed neutral")
    elif polarity > 0:
        await ctx.send("That message seemed positive")
    else:
        await ctx.send("That message seemed negative")


# @bot.command()
# async def usersentiment(ctx, user: discord.Member = None):
#     '''display a histogram distribution of the polarity of a
#     given user's messages in all text channels'''

#     polarities = []
#     for channel in ctx.guild.text_channels:
#         async for message in channel.history(limit=1000):
#             if message.author == user:
#                 blob = TextBlob(message.content)
#                 polarity = blob.sentiment.polarity
#                 polarities.append(polarity)
#     df = pd.DataFrame({'polarity': polarities})
#     histogram = df.plot.hist()
#     display_plot(ctx, histogram)


@bot.command()
async def favoriteemoji(ctx, user: discord.Member = None):
    '''output most used emoji of a given user in all text channels'''

    emojis = {}
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            if message.author == user:
                for react in message.reactions:
                    if not react.emoji in emojis:
                        emojis[react.emoji] = 1
                    else:
                        emojis[react.emoji] += 1
            else:
                await ctx.send("You must select a user")
    sorted_emojis = dict(sorted(emojis.items(), key=lambda item: item[1]))
    await ctx.send(f"User's favorite emoji is {list(sorted_emojis.keys())[-1]}")


@bot.command()
async def weeklystats(ctx):
    '''display stats about the last week of the server text channels'''

    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    counter = 0
    users = []
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000, before=today, after=one_week_ago):
            if not message.author in users:
                users.append(message.author)
            counter += 1
    await ctx.send(f"{counter} messages in the last week by {len(users)} users")


@bot.command()
async def engagingmessage(ctx, message_id):
    ''' Get reaction counts for a message '''
    msg = await ctx.fetch_message(message_id)
    reaction_counts = 0
    for reaction in msg.reactions:
        reaction_counts += reaction.count
    embed = discord.Embed(description=msg.content)
    embed.set_author(name=msg.author.display_name)
    embed.set_footer(text=f"{reaction_counts} reactions to messasge")
    await ctx.send(embed=embed)


# @bot.command()
# async def reactiontimes(ctx):
#     ''' Plot out amount of reactions on a server by week '''
#     counter = 0
#     reaction_messages = []
#     for channel in ctx.guild.text_channels:
#         async for message in channel.history(limit=1000):
#             if message.reactions:
#                 message_react_counts = 0
#                 for reaction in message.reactions:
#                     message_react_counts += 1
#                 reaction_messages.append({'content': message.content,
#                                           'time': message.created_at,
#                                           'author': message.author.name,
#                                           'reaction_count': message_react_counts})
#     df = pd.DataFrame(reaction_messages)
#     df['time'] = pd.to_datetime(df['time'])
#     df = df.set_index('time')
#     df = df.resample('W').sum()

#     time_chart = df.plot(marker='.')
#     display_plot(ctx, time_chart)


@bot.command()
async def lastweekreacts(ctx, threshold):
    ''' Display messages that have passed a user-provided threshold of n reacts in the last week '''
    threshold = int(threshold)
    msgs = []
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    message_react_counts = 0
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000, after=one_week_ago):
            if message.reactions:
                print(message.content)
                # message_react_counts = 0
                for reaction in message.reactions:
                    message_react_counts += 1
                if message_react_counts >= threshold:
                    msgs.append(message)
    for msg in msgs:
        reaction_counts = 0
        for reaction in msg.reactions:
            reaction_counts += reaction.count
        embed = discord.Embed(description=msg.content)
        embed.set_author(name=msg.author.display_name)
        embed.set_footer(text=f"{reaction_counts} reactions to messasge")
        await ctx.send(embed=embed)

bot.run(TOKEN, bot=True)
