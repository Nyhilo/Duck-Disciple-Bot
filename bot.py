import asyncio
import discord
from discord.ext import commands

import sys
import os

from dotenv import load_dotenv

from config.config import PREFIX, CACHE_FOLDER
from core.log import log

###########
# Globals #
###########

load_dotenv()
TOKEN = os.getenv('TOKEN')


#########
# Setup #
#########

help_command = commands.DefaultHelpCommand(no_category='Other')
intents = discord.Intents.default()
intents.message_content = True
activity = discord.ActivityType.listening
client = commands.Bot(command_prefix=PREFIX,
                      description=(
                        'Cartogrpher shows you the way. A general-use bot for '
                        'the Infinite Nomic discord server.'),
                      help_command=help_command,
                      activity=discord.Activity(type=activity, name=PREFIX),
                      intents=intents
                      )


@client.event
async def on_ready():
    log.info(f'Python version {sys.version}')
    log.info(f'Discord API version:  {discord.__version__}')
    log.info(f'Logged in as {client.user.name}')
    log.info('Bot is ready!')


##############
# Initialize #
##############

@client.event
async def setup_hook():
    log.info("Starting bot...")

    # Setup caching folder
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

    # Setup database
    import core.db.reminders_db as reminders_db
    reminders_db.set_tables()
    import core.db.pools_db as pools_db
    pools_db.set_tables()

    # Load cogs
    cogs = ['cogs.cycle', 'cogs.image_manipulation', 'cogs.reminders', 'cogs.miscellaneous', 'cogs.loot']

    for cog in cogs:
        try:
            log.info(f'Loading extension {cog}')
            await client.load_extension(cog)
        except Exception as e:
            log.exception(e)


# Let it fly
client.run(TOKEN, log_handler=None)
