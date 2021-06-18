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
          'discord mentions may produce unexpected results.')
)
async def sha(ctx, *, message):
    try:
        log.debug(message)
        hash = shalib.get_sha_256(message)
        await ctx.send(f'The hash for the above message is:\n{hash}')
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


##############
# Initialize #
##############

def init():
    log.info("Starting bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
