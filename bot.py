import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv


# Globals #
load_dotenv()
TOKEN = os.getenv('TOKEN')


# Setup #
bot = commands.Bot(command_prefix="&", description='Duck bot go quack.')


@bot.event
async def on_ready():
    print('Python version', sys.version)
    print('Discord API version: ' + discord.__version__)
    print('Logged in as', bot.user.name)
    print('Bot is ready!')


# Commands #
@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")


def init():
    print("Starting bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
