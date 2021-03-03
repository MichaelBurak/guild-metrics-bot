# Guild Metrics Bot

## A [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html#getting-started) Bot for Server/Channel/Message/User analysis focusing on Natural Language PRocessing

- Functionality:
- General:
  - Scrape all messages and dump content, time, author,
    sentiment polarity into mongodb atlas instance
- Stats:
  - Display countplot of most frequent message authors in
    channel the command is run in
  - Give a count of each emoji used in text channels on a server/guild
  - Output most used emoji of a given user in all text channels on a server
  - Display number of messages in the last week by number of users on a server
  - Get reaction counts for a message
  - Plot out amount of reactions on a server by week
  - Display messages that have passed a user-provided threshold of n reacts in the last week
- Sentiment analysis

  - Display sentiment analysis polarity by author on barplot
  - Give the TextBlob polarity of a passed in string
    as positive, neutral or negative
  - Display a histogram distribution of the polarity of a
    given user's messages in all text channels on a server

- Installation:

  - Clone the repo and set up a Discord bot(plenty of good tutorials around for this, I'll try to add my favorite(s) in the future to this README), invite to server
  - Set up a MongoDB Atlas cluster, preferably, though you could change it up to use MongoDB differently, Atlas has proven to work well for this bot, with a base "test" database and "text" cluster, but I'd suggest changing these names for your own use case :) .

- To Do:

  - Better repo organization in bot.py
  - Splitting out functions
  - Implementing cogs
  - Working to speed up some commands that take longer with cython/multithreading/etc.
  - Lots of stats and viz!

- License:
  - Uhhh MIT? I don't much care, have fun with it!
