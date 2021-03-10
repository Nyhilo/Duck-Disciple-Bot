import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv

import config
from log import log
import generator
import scraper


# Globals #
load_dotenv()
TOKEN = os.getenv('TOKEN')


# Setup #
bot = commands.Bot(command_prefix=config.PREFIX,
                   description='Duck bot go quack.')


@bot.event
async def on_ready():
    log.info(f'Python version {sys.version}')
    log.info(f'Discord API version:  {discord.__version__}')
    log.info(f'Logged in as {bot.user.name}')
    log.info('Bot is ready!')


# Commands #
@bot.command()
async def name(ctx):
    log.info(f'Name request by {ctx.author}')

    name = generator.get_random_duck_name()

    if name is None:
        error = ('An error occured getting your duck name :(\n'
                 'Please send a message to my author and let them know.')

        await ctx.send(error)
    else:
        await ctx.send(f'A duck name for you! `{name}`')


@bot.command()
async def duck(ctx):
    cached_ducks = scraper.get_ducks(False)
    duck_count = len(cached_ducks)

    # TODO: Get random number from dice bot
    random_number = 18   # Guaranteed to be random

    msg = scraper.get_player_duck(random_number, cached_ducks, False)

    await ctx.send(msg)


def init():
    log.info("Starting bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
