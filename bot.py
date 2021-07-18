import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv
# from random import randint

import config
from log import log
import nomic_time
import sha as shalib
import cards
import utils


###########
# Globals #
###########

load_dotenv()
TOKEN = os.getenv('TOKEN')


#########
# Setup #
#########

help_command = commands.DefaultHelpCommand(no_category='Commands')
bot = commands.Bot(command_prefix=config.PREFIX,
                   description=('Poker bot doubles down. A general-use bot '
                                'for the Infinite Nomic on discord.'),
                   help_command=help_command)


@bot.event
async def on_ready():
    log.info(f'Python version {sys.version}')
    log.info(f'Discord API version:  {discord.__version__}')
    log.info(f'Logged in as {bot.user.name}')
    log.info('Bot is ready!')


############
# Commands #
############

@bot.command(
    brief='Get current time and day in UTC',
    help='Get current time and day in UTC'
)
async def time(ctx):
    try:
        await ctx.send(nomic_time.get_current_utc_string())
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(
    brief='Gets the SHA256 for a given input.',
    help=('Gets the SHA256 hash for a given input. Note that including '
          'discord mentions may produce unexpected results.\n'
          'Inputs may be surrounded by double quotes to ensure expected '
          'whitespace.')
)
async def sha(ctx, *, message=None):
    if message is None:
        await ctx.send("Please include the message you would like me to hash.")
        return

    try:
        filteredMessage = utils.trim_quotes(message)
        hash = shalib.get_sha_256(filteredMessage)
        await ctx.send(f'The hash for the above message is:\n{hash}')
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(
    brief='Draw a number of cards.',
    help=('Automatically roll some dice and report back the dice rolls and '
          'the cards generated from those dice rolls. Will return 1 set of 1 '
          'card by default. First argument is number of cards, second argument '
          'is size of card sets. Maximum draw is 100.')
)
async def draw(ctx, number=1, size=1):
    if number * size < 1:
        return await ctx.send('Positive integers only please.')

    maxcards = 100
    if number * size > maxcards:
        return await ctx.send('Sorry, maximum number of cards per draw '
                              f'is {maxcards}.')

    try:
        msg = cards.draw_random_card_sets(number, size)
        await ctx.send(msg)
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


@draw.error
async def drawpairs_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Please provide an integer of cards to draw.')


##############
# Initialize #
##############

def init():
    log.info("Starting bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
