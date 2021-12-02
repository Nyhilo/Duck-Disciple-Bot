import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv

from config.config import PREFIX
from core.log import log

###########
# Globals #
###########

load_dotenv()
TOKEN = os.getenv('TOKEN')


#########
# Setup #
#########

help_command = commands.DefaultHelpCommand(no_category='Commands')
bot = commands.Bot(command_prefix=PREFIX,
                   description=('Day Trader gets those tendies. A general-use bot '
                                'for the Infinite Nomic discord server.'),
                   help_command=help_command)


@bot.event
async def on_ready():
    log.info(f'Python version {sys.version}')
    log.info(f'Discord API version:  {discord.__version__}')
    log.info(f'Logged in as {bot.user.name}')
    log.info('Bot is ready!')


##############
# Initialize #
##############

def init():
    log.info("Starting bot...")

    from core.db import set_tables
    set_tables()

    cogs = ['cogs.image_manipulation', 'cogs.reminders', 'cogs.miscellaneous']

    for cog in cogs:
        try:
            log.info(f'Loading extension {cog}')
            bot.load_extension(cog)
        except Exception as e:
            log.exception(e)

    bot.run(TOKEN)


if __name__ == "__main__":
    init()
