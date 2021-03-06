import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv

import config
from log import log

# Globals #
load_dotenv()
TOKEN = os.getenv('TOKEN')


# Setup #
bot = commands.Bot(command_prefix=config.PREFIX,
                   description='Duck bot go quack.')


@bot.event
async def on_ready():
    log.info('Python version', sys.version)
    log.info('Discord API version: ', discord.__version__)
    log.info('Logged in as', bot.user.name)
    log.info('Bot is ready!')


# Commands #
@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")


def init():
    log.info("Starting bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
