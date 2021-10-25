import discord
from discord.ext import commands, tasks

import sys
import os
import asyncio

from dotenv import load_dotenv
# from random import randint

import config
from log import log
import nomic_time
import sha as shalib
import utils
import image
import reminders


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

    task_check.start()


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


@bot.command(
    brief='Have the bot remind you about something in the future',
    help=('Usage: <number> <second(s)|minute(s)|hour(s)|day(s)|week(s)> [message]\n'
          'Will save a reminder and reply in the same channel at the specifid point in the future. '
          'Long-term reminders poll every minute. Adding a message is optional, '
          'and will be echoed to you in the case that your message gets deleted.')
)
async def remind(ctx, *, message=None):
    if not message:
        return await ctx.send(f'Please see `{config.PREFIX}help remind` for details on how to use this command.')

    # Get Info to set
    userId = ctx.message.author.mention
    createdAt = ctx.message.created_at
    messageId = ctx.message.id
    channelId = ctx.channel.id
    remindAfter, msg = reminders.parse_remind_message(message)

    if remindAfter is None:
        return await ctx.send(msg)

    if remindAfter.total_seconds() < 10:
        return await ctx.send("C'mon, less than 10 seconds is just silly.")

    if reminders.can_quick_remind(remindAfter):
        seconds = remindAfter.total_seconds()
        log.info(f'Performing quick remind in {seconds} seconds')
        await ctx.send("Okay, I'll remind you.")
        await asyncio.sleep(remindAfter.total_seconds())
        return await ctx.reply('Hey, reminding you about this thing.')

    try:
        responseMsg = reminders.set_new_reminder(userId, messageId, channelId, createdAt, remindAfter, msg)
        log.info(responseMsg.split('\n')[0])
        await ctx.send(responseMsg)
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(
    brief='Delete a set reminder',
    help='Specify the id of a long-term reminder to remove it. Only admins and '
         'the original author of the reminder can delete them.'
)
async def forget(ctx, rowId=None):
    if not rowId:
        return await ctx.send('Please include the id of the reminder to forget.')

    try:
        responseMsg = reminders.unset_reminder(rowId, ctx.message.author.id)
        await ctx.send(responseMsg)
    except Exception as e:
        log.error(e)
        await ctx.send(config.GENERIC_ERROR)


@tasks.loop(minutes=1)
async def task_check():
    # Get all active tasks
    tasks = reminders.check_for_triggered_reminders()

    for task in tasks:
        mention = task['UserId']
        msg = task['RemindMsg']
        rowId = task['rowid']
        channelId = task['ChannelId']
        channel = bot.get_channel(channelId)
        if channel is None:
            log.info(f'Channel with id {channelId} does not exist. Setting reminder with id {rowId} to inactive...')
            if rowId:
                unsetMsg = reminders.unset_reminder(rowId, overrideId=True)
                log.info(unsetMsg)
            continue

        try:
            replyTo = await channel.fetch_message(task['MessageId'])
            await replyTo.reply(f'{mention}, reminding you of the message you sent here.')
        except discord.NotFound:
            _msg = f'\n\n"{msg}"' if msg else ''
            await channel.send(f'{mention}, reminding you of a reminder you set in this channel.{_msg}')

        log.info(reminders.unset_reminder(rowId, overrideId=True))


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

    from db import set_tables
    set_tables()

    bot.run(TOKEN)


if __name__ == "__main__":
    init()
