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
import utils
import image
import db


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
    brief='Trungifies an image',
    help=('Attach or link to an image to trungify it.\n'
          'You can also reply another message that has an image with this '
          'command to trungify that image instead.')
)
async def trungify(ctx):
    commandName = f'{config.PREFIX}trungify'

    async def get_image_source():
        # Check if the message contains an image
        message = ctx.message
        if (
            len(message.attachments) > 0 and
            any(message.attachments[0].filename.endswith(e) for e in config.IMAGE_EXTENSIONS)
           ):
            return message.attachments[0].url

        if any(message.content.endswith(e) for e in config.IMAGE_EXTENSIONS):
            return utils.strip_command(message.content, commandName)

        # Check if a replied to message contains an image
        if message.reference:
            reply = await ctx.channel.fetch_message(ctx.message.reference.message_id)

            if (
                len(reply.attachments) > 0 and
                any(reply.attachments[0].filename.endswith(e) for e in config.IMAGE_EXTENSIONS)
               ):
                return reply.attachments[0].url

            if any(reply.content.endswith(e) for e in config.IMAGE_EXTENSIONS):
                return utils.strip_command(reply.content, commandName)

        # No valid image found
        return None

    source = await get_image_source()
    if source is None:
        await ctx.send('Either I don\'t support that image type or you didn\'t send or reply to an image.')
        return

    try:
        async with ctx.typing():
            image.trungify_and_save(source, config.TRUNGIFY_CACHE)

            with open(config.TRUNGIFY_CACHE, 'rb') as file:
                f = discord.File(file, filename=config.TRUNGIFY_CACHE)

            await ctx.send(file=f)
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command()
async def remind(ctx, *, message=None):
    userId = ctx.message.author.name
    timestamp = int(ctx.message.created_at.timestamp())
    remindAt = timestamp + 5000
    id = db.save_reminder(userId, timestamp, remindAt, message)
    log.info(id)
    await ctx.send(f'Reminder created with id {id}')


# Leaving this for re-implementation in the future
# @bot.command(
#     brief='Draw a number of cards.',
#     help=('Automatically roll some dice and report back the dice rolls and '
#           'the cards generated from those dice rolls. Will return 1 set of 1 '
#           'card by default. First argument is number of cards, second argument '
#           'is size of card sets. Maximum draw is 100.\n')
# )
# async def draw(ctx, number=1, size=1):
#     if number * size < 1:
#         return await ctx.send('Positive integers only please.')

#     maxcards = 100
#     if number * size > maxcards:
#         return await ctx.send('Sorry, maximum number of cards per draw '
#                               f'is {maxcards}.')

#     try:
#         msg = cards.draw_random_card_sets(number, size)
#         await ctx.send(msg)
#     except Exception as e:
#         log.error(e)
#         await ctx.send(config.GENERIC_ERROR)


##############
# Initialize #
##############

def init():
    log.info("Starting bot...")
    db.set_tables()

    bot.run(TOKEN)


if __name__ == "__main__":
    init()
