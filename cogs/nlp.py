import discord
from discord.ext import commands
from discord.ext.commands import Cog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
# from bot import display_plot
from bot import db, text_col

import os

"""A simple cog example with simple commands. Showcased here are some check decorators, and the use of events in cogs.
For a list of inbuilt checks:
http://dischttp://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#checksordpy.readthedocs.io/en/rewrite/ext/commands/api.html#checks
You could also create your own custom checks. Check out:
https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L689
For a list of events:
http://discordpy.readthedocs.io/en/rewrite/api.html#event-reference
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#event-reference
"""


class NlpCog(commands.Cog, name="Nlp Commands"):
    """NlpCog"""
    def __init__(self, bot):
        self.bot = bot

    async def display_plot(self,ctx, plot_type, path="plot.png"):
        plot = plot_type
        plt.tight_layout()
        fig = plot.get_figure()
        fig.savefig(path)

        await ctx.send(file=discord.File(path))
        os.remove(path)


    @commands.command(name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, *, our_input: str):
        """A simple command which repeats our input.
        In rewrite Context is automatically passed to our commands as the first argument after self."""

        await ctx.send(our_input)

    @commands.command(name="mostfreq")
    async def mostfreq(self, ctx):
        '''Display countplot of most frequent message authors in
        command channel'''
        df = pd.DataFrame(columns=['author'])
        for channel in ctx.guild.text_channels:
            async for message in channel.history(limit=1000):
                # if not message.author.bot:
                df = df.append(
                    {'author': message.author.name}, ignore_index=True)

        countplot = sns.countplot(
            y="author", data=df, order=df['author'].value_counts().iloc[:3].index)

        await self.display_plot(ctx,countplot)
        # display_plot(ctx, countplot)

    @commands.command(name="polarity")
    async def polarity(self,ctx):
        '''display polarity by author on barplot
        currently grouped by mean, needs testing, 
        requires buildpack or nltk.txt for textblob when deploying to heroku'''
        # await message = ctx.send("Loading polarity...")
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
        await self.display_plot(ctx, barplot)

    # @commands.command(name='repeat', aliases=['copy', 'mimic'])
    # async def do_repeat(self, ctx, *, our_input: str):
    #     """A simple command which repeats our input.
    #     In rewrite Context is automatically passed to our commands as the first argument after self."""

    #     await ctx.send(our_input)

    # @commands.command(name='add', aliases=['plus'])
    # @commands.guild_only()
    # async def do_addition(self, ctx, first: int, second: int):
    #     """A simple command which does addition on two integer values."""

    #     total = first + second
    #     await ctx.send(f'The sum of **{first}** and **{second}**  is  **{total}**')

    # @commands.command(name='me')
    # @commands.is_owner()
    # async def only_me(self, ctx):
    #     """A simple command which only responds to the owner of the bot."""

    #     await ctx.send(f'Hello {ctx.author.mention}. This command can only be used by you!!')

    # @commands.command(name='embeds')
    # @commands.guild_only()
    # async def example_embed(self, ctx):
    #     """A simple command which showcases the use of embeds.
    #     Have a play around and visit the Visualizer."""

    #     embed = discord.Embed(title='Example Embed',
    #                           description='Showcasing the use of Embeds...\nSee the visualizer for more info.',
    #                           colour=0x98FB98)
    #     embed.set_author(name='MysterialPy',
    #                      url='https://gist.github.com/MysterialPy/public',
    #                      icon_url='http://i.imgur.com/ko5A30P.png')
    #     embed.set_image(url='https://cdn.discordapp.com/attachments/84319995256905728/252292324967710721/embed.png')

    #     embed.add_field(name='Embed Visualizer', value='[Click Here!](https://leovoel.github.io/embed-visualizer/)')
    #     embed.add_field(name='Command Invoker', value=ctx.author.mention)
    #     embed.set_footer(text='Made in Python with discord.py@rewrite', icon_url='http://i.imgur.com/5BFecvA.png')

    #     await ctx.send(content='**A simple Embed for discord.py@rewrite in cogs.**', embed=embed)

    # @commands.Cog.listener()
    # async def on_member_ban(self, guild, user):
    #     """Event Listener which is called when a user is banned from the guild.
    #     For this example I will keep things simple and just print some info.
    #     Notice how because we are in a cog class we do not need to use @bot.event
    #     For more information:
    #     http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_member_ban
    #     Check above for a list of events.
    #     """

    #     print(f'{user.name}-{user.id} was banned from {guild.name}-{guild.id}')

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.


def setup(bot):
    bot.add_cog(NlpCog(bot))

