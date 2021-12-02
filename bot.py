import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv
# from random import randint

import config.config as config
from core.log import log
import core.nomic_time as nomic_time
import core.sha as shalib
import core.utils as utils


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
                   description=('Day Trader gets those tendies. A general-use bot '
                                'for the Infinite Nomic discord server.'),
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
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(
    brief='Gets the SHA256 for a given input',
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
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(brief='Stop doing nomic.', aliases=['sdn'])
async def stopdoingnomic(ctx):
    async with ctx.typing():
        with open('stop_doing_nomic.png', 'rb') as file:
            f = discord.File(file, filename='stop_doing_nomic.png')

        await ctx.send(file=f)


@bot.command(
    brief='Draw a number of cards.',
    help=('Automatically roll some dice and report back the dice rolls and '
          'the cards generated from those dice rolls. Will return 1 set of 1 '
          'card by default. First argument is number of cards, second argument '
          'is size of card sets. Maximum draw is 100.\n')
)
async def draw(ctx, number=1, size=1):
    if number * size < 1:
        return await ctx.send('Positive integers only please.')

    maxcards = 50
    if number * size > maxcards:
        return await ctx.send('Sorry, maximum number of cards per draw '
                              f'is {maxcards}.')

    try:
        await ctx.send(('Here are your cards!' if number * size > 1 else 'Here is your card!'))
        await ctx.send(utils.draw_random_card_sets(number, size))
    except Exception as e:
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(
    brief='Get unix timestamp for date string.',
    help=('Literally just runs the given string against the python-dateutil library. '
          'Can generally be as vague or specific as you want.')
)
async def timestamp(ctx, *, message=None):
    try:
        timestamp = nomic_time.get_datestring_timestamp(message)
    except Exception:
        return await ctx.send('Whoops, I did\'t recognize the date format you sent. Try something else.')

    await ctx.send(f'Here is your timestamp for <t:{timestamp}> your time: `{timestamp}`')


##############
# Initialize #
##############

def init():
    log.info("Starting bot...")

    from core.db import set_tables
    set_tables()

    cogs = ['cogs.image_manipulation', 'cogs.reminders']

    for cog in cogs:
        try:
            log.info(f'Loading extension {cog}')
            bot.load_extension(cog)
        except Exception as e:
            log.exception(e)

    bot.run(TOKEN)


if __name__ == "__main__":
    init()
