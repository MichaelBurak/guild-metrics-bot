# bot.py
# import logging
from pymongo import MongoClient
import os
# import random
# import re

import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.utils import get
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from pymongo import MongoClient

# env var handling of token and testing Google Sheet
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URL = os.getenv("MONGO_URL")
cluster = MongoClient(MONGO_URL)

db = cluster["test"]

text_col = db["text"]

# intents = discord.Intents.all()
# intents.members = True

bot = commands.Bot(command_prefix="^")

# on ready, add users


@bot.command()
async def test(ctx):
    await ctx.send("server metrics bot test")


@bot.command()
async def channellist(ctx):
    channels = ctx.guild.text_channels
    channel_names = [c.name for c in channels]

    await ctx.send(channel_names)


@bot.command()
async def mostfreq(ctx):
    channel = ctx.channel
    counter = 0
    df = pd.DataFrame(columns=['author'])
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            # if not message.author.bot:
            df = df.append(
                {'author': message.author.name}, ignore_index=True)

    countplot = sns.countplot(
        y="author", data=df, order=df['author'].value_counts().iloc[:3].index)
    plt.tight_layout()
    fig = countplot.get_figure()
    fig.savefig("author.png")

    await ctx.send(file=discord.File('author.png'))
    os.remove('author.png')


@bot.command()
async def mongscrape(ctx):
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


bot.run(TOKEN)
