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
from transformers import pipeline
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

# check functions


def check(message):
    return message.author.id == some_author_id


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

# requires buildpack or nltk.txt


@bot.command()
async def polarity(ctx):
    msgs = []
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            blob = TextBlob(message.content)
            polarity = blob.sentiment.polarity
            msgs.append({
                'author': message.author.name,
                'polarity': polarity})
    df = pd.DataFrame(msgs)
    df = df.groupby(['author']).sum()

    barplot = sns.barplot(y=df.index, x=df.polarity)
    plt.tight_layout()
    fig = barplot.get_figure()
    fig.savefig("polarity.png")

    await ctx.send(file=discord.File('polarity.png'))
    os.remove('polarity.png')


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

'''huggingface doens't play nice w/heroku
@bot.command()
async def sentiment(ctx):
    nlp = pipeline("sentiment-analysis")
    result = nlp(ctx.message.content)[0]
    await ctx.send(f"That message seemed {result['label'].lower()}")
'''


@bot.command()
async def sentiment(ctx):
    blob = TextBlob(ctx.message.content)
    polarity = blob.sentiment.polarity
    if polarity == 0:
        await ctx.send("That message seemed neutral")
    elif polarity > 0:
        await ctx.send("That message seemed positive")
    else:
        await ctx.send("That message seemed negative")


@bot.command()
async def usersentiment(ctx, user: discord.Member = None):
    polarities = []
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            if message.author == user:
                blob = TextBlob(message.content)
                polarity = blob.sentiment.polarity
                polarities.append(polarity)
    df = pd.DataFrame({'polarity': polarities})
    histogram = df.plot.hist()
    plt.tight_layout()
    fig = histogram.get_figure()
    fig.savefig("polarity.png")

    await ctx.send(file=discord.File('polarity.png'))
    os.remove('polarity.png')


@bot.command()
async def favoriteemoji(ctx, user: discord.Member = None):
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
    # print(sorted_emojis)
    await ctx.send(f"User's favorite emoji is {list(sorted_emojis.keys())[-1]}")


# probably best to be an API call and return as loading is slow
# @bot.command()
# async def summarizeuser(ctx, user: discord.Member = None):
#     summarizer = pipeline("summarization")

#     if not user:
#         await ctx.send('You must specify a user')
#     else:
#         messages = await channel.history(limit=100, check=check).flatten()
#         messages = ' '.join(messages)
#         summary = summarizer(messages, max_length=130,
#                              min_length=30, do_sample=False)
#         await ctx.send(summary)

bot.run(TOKEN)
