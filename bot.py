# bot.py
# import logging
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

# env var handling of token and testing Google Sheet
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

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

bot.run(TOKEN)
