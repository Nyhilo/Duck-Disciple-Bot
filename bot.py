import discord
from discord.ext import commands, tasks

import sys
import os
import asyncio
import re

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
                   description=('Day Trader gets those tendies. A general-use bot '
                                'for the Infinite Nomic discord server.'),
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
    brief='Trungifies an image',
    help=('Attach or link to an image to trungify it.\n'
          'You can also reply another message that has an image with this '
          'command to trungify that image instead.'),
    aliases=['trung', 'tr', 'triangle', 'trungle', 'trunglo']
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
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


@bot.command(
    brief='Detrungifies an image',
    help=('Attach or link to an image to detrungify it.\n'
          'You can also reply another message that has an image with this '
          'command to detrungify that image instead.'),
    aliases=['detrung', 'dtr', 'dt', 'bigbrain', 'antitrung']
)
async def detrungify(ctx):
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
            image.detrungify_and_save(source, config.TRUNGIFY_CACHE)

            with open(config.TRUNGIFY_CACHE, 'rb') as file:
                f = discord.File(file, filename=config.TRUNGIFY_CACHE)

            await ctx.send(file=f)
    except Exception as e:
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


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


@bot.command(
    brief='Have the bot remind you about something in the future',
    help=(f'Usages: &remind [number] [second(s)|minute(s)|hour(s)|day(s)|week(s)] <message>\n'
          f'        &remind [timestamp] <message>\n'
          f'        &remind [datestring]; <message>\n'
          'Will save a reminder and reply in the same channel at the specified point in the future.\n'
          'Long-term reminders are checked once per minute. Adding a message is optional, '
          'and will be echoed back to you.\n\n'
          'Escape users and roles in the creation message with User#ID and @"Role" respectively.\n'
          'For example, User#0000 and @"everyone" will be echoed back as @User#0000 and @everyone.\n\n'
          'Examples:\n'
          f"\t{config.PREFIX}remind 5 days\n"
          f"\t{config.PREFIX}remind 7 days Hey @\"everyone\" it's time!\n"
          f"\t{config.PREFIX}remind december 25th, 8:00am; don't forget to do the thing.\n"
          f"\t{config.PREFIX}remind 1640419200 The time has come\n"
          ),
    aliases=['rem', 'member', 'rember']
)
async def remind(ctx, *, message=None):
    if not message:
        return await ctx.send(f'Please see `{config.PREFIX}help remind` for details on how to use this command.')

    # Get Info to set
    userId = ctx.message.author.id
    createdAt = ctx.message.created_at
    messageId = ctx.message.id
    channelId = ctx.channel.id
    remindAfter, _msg = reminders.parse_remind_message(message, createdAt)
    msg = await filter_escaped_mentions(ctx, _msg)

    return await handle_set_reminder(ctx, userId, createdAt, messageId, channelId, remindAfter, msg)


async def handle_set_reminder(ctx, userId, createdAt, messageId, channelId, remindAfter, msg):
    if remindAfter is None:
        return await ctx.send(msg)

    if remindAfter.total_seconds() < 10:
        return await ctx.send("C'mon, less than 10 seconds is just silly.")

    if reminders.can_quick_remind(remindAfter):
        seconds = remindAfter.total_seconds()
        secondsAgo = nomic_time.get_timestamp(createdAt)
        log.info(f'Performing quick remind in {seconds} seconds')
        await ctx.send("Okay, I'll remind you.")
        await asyncio.sleep(remindAfter.total_seconds())

        _msg = f'\n\n"{msg}"' if msg and len(msg) < 1000 else ''
        try:
            replyTo = await ctx.fetch_message(messageId)
            return await replyTo.reply(f'Hey, reminding you about this thing.{_msg}')
        except discord.NotFound:
            return await ctx.send(f'<@!{userId}>, reminding you of a reminder you '
                                  f'set in this channel <t:{secondsAgo}:R>.{_msg}')

    try:
        responseMsg = reminders.set_new_reminder(userId, messageId, channelId, createdAt, remindAfter, msg)
        log.info(responseMsg.split('\n')[0])
        await ctx.send(responseMsg)
    except Exception as e:
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


@tasks.loop(minutes=1)
async def task_check():
    # Get all active tasks
    tasks = reminders.check_for_triggered_reminders()

    for task in tasks:
        userId = task['UserId']
        createdAt = task['CreatedAt']
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

        _msg = f'\n\n"{msg}"' if msg else ''
        try:
            replyTo = await channel.fetch_message(task['MessageId'])
            await replyTo.reply(f'<@!{userId}>, reminding you of the message you sent here.{_msg}')
        except discord.NotFound:
            await channel.send(f'<@!{userId}>, reminding you of a reminder you '
                               f'set in this channel <t:{createdAt}:R>.{_msg}')

        log.info(reminders.unset_reminder(rowId, overrideId=True))


@bot.command(
    brief='Delete a set reminder',
    help=('Specify the id of a long-term reminder to remove it. Only admins and '
          'the original author of the reminder can delete them.'),
    aliases=['forgor']
)
async def forget(ctx, rowId=None):
    if not rowId:
        return await ctx.send('Please include the id of the reminder to forget.')

    guildId = ctx.guild.id if ctx.guild else None

    try:
        responseMsg = reminders.unset_reminder(rowId, ctx.message.author.id, guildId)
        await ctx.send(responseMsg)
    except Exception as e:
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


###########
# Helpers #
###########

memberConverter = commands.MemberConverter()
roleConverter = commands.RoleConverter()


async def filter_escaped_mentions(ctx, message):
    async def resolve_mention(converter, mention):
        try:
            member = await converter.convert(ctx, mention)
            return member.mention
        except commands.BadArgument:
            return mention

    # User mentions in the form of Name#0000
    matches = re.finditer(r'\b\S+#\d+\b', message)
    for match in matches:
        replace = await resolve_mention(memberConverter, match.group())
        message = message.replace(match.group(), replace)

    # Role mentions in the form of @"Role"
    matches = re.finditer(r'@".*?"', message)
    for match in matches:
        replace = await resolve_mention(roleConverter, match.group()[2:-1])
        message = message.replace(match.group(), replace)

    return message


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
