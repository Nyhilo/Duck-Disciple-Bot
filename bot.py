import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv
from random import randint

import config
from log import log
import generator
import scraper


# Globals #
load_dotenv()
TOKEN = os.getenv('TOKEN')


# Setup #
help_command = commands.DefaultHelpCommand(no_category='Commands')
bot = commands.Bot(command_prefix=config.PREFIX,
                   description='Duck bot go quack.',
                   help_command=help_command)


@bot.event
async def on_ready():
    log.info(f'Python version {sys.version}')
    log.info(f'Discord API version:  {discord.__version__}')
    log.info(f'Logged in as {bot.user.name}')
    log.info('Bot is ready!')


# Commands #
@bot.command(
    brief='Generate a random duck name.',
    help=('Generate a random duck name.\n'
          'Duck names are generated from the api at '
          f'{config.NAME_GENERATOR_URL}')
)
async def name(ctx):
    log.info(f'Name request by {ctx.author}')

    name = generator.get_random_duck_name()

    if name is None:
        error = ('An error occured getting your duck name :(\n'
                 'Please send a message to my author and let them know.')

        await ctx.send(error)
    else:
        await ctx.send(f'A duck name for you! `{name}`')


# TODO: Let command accept number to acquire duck
# TODO: Make version of command that gets unnamed ducks as well
# TODO: Handle possible errors
@bot.command(
    brief='Fetch a random or specific nammed duck.',
    help=('Fetch a random named duck from the Round 9 Gamestate wiki.\n'
          'Use `duck <number>` to fetch a duck with a specific dice roll.')
)
async def duck(ctx, *, arg=None):
    log.info(f'Roll requested by {ctx.author}')

    cached_ducks = scraper.get_ducks(False)
    duck_count = len(cached_ducks)

    if arg is None:
        random_number = randint(1, duck_count)
    else:
        try:
            random_number = int(arg)
        except ValueError:
            log.info(f'Invalid value sent by user. Value: {arg}')
            return await ctx.send(f'Value: `{arg}` is not an integer that '
                                  'I can find a duck with.')

    if arg and random_number < 1:
        log.info(f'Number recieved is less than 1: {random_number}')
        return await ctx.send('Please give a number greater than 0.')

    if arg and random_number > duck_count:
        log.info(f'Number received exceeds number of ducks: {random_number}')
        return await ctx.send('The number you gave is larger than the '
                              'number of available ducks. Please give a '
                              f'number between 1 and {duck_count}.')

    msg = scraper.get_player_duck(random_number, cached_ducks, False)

    await ctx.send(msg)


def init():
    log.info("Starting bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
