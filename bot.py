# bot.py
# import logging
from pymongo import MongoClient
import os

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
# from transformers import pipeline -- add text summary later

# env var handling of token and mongo connection
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URL = os.getenv("MONGO_URL")
cluster = MongoClient(MONGO_URL)

db = cluster["test"]

text_col = db["text"]

bot = commands.Bot(command_prefix="^")


@bot.command()
async def test(ctx):
    await ctx.send("server metrics bot test")


@bot.command()
async def mostfreq(ctx):
    '''Display countplot of most frequent message authors in
    command channel, displaying twice?'''
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

# requires buildpack or nltk.txt for textblob


@bot.command()
async def polarity(ctx):
    '''display polarity by author on barplot
    currently grouped by mean, needs testing'''

    msgs = []
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=1000):
            blob = TextBlob(message.content)
            polarity = blob.sentiment.polarity
            msgs.append({
                'author': message.author.name,
                'polarity': polarity})
    df = pd.DataFrame(msgs)
    df = df.groupby(['author']).mean()

    barplot = sns.barplot(y=df.index, x=df.polarity)
    plt.tight_layout()
    fig = barplot.get_figure()
    fig.savefig("polarity.png")

    await ctx.send(file=discord.File('polarity.png'))
    os.remove('polarity.png')


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


@bot.command()
async def usersentiment(ctx, user: discord.Member = None):
    '''display a histogram distribution of the polarity of a 
    given user's messages in all text channels'''

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

bot.run(TOKEN)
