import discord
from discord.ext import commands, tasks
import asyncio
import re
import time

import config.config as config

from core.log import log
import core.reminders as reminders
import core.nomic_time as nomic_time


class Reminders(commands.Cog, name='Reminders'):
    '''
    A collection of commands related to setting reminders.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
        self.channel_time.start()

    @commands.command(
        brief='Have the bot remind you about something',
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
    async def remind(self, ctx, *, message=None):
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

    @commands.command(
        brief='Delete a set reminder',
        help=('Specify the id of a long-term reminder to remove it. Only admins and '
              'the original author of the reminder can delete them.'),
        aliases=['forgor']
    )
    async def forget(self, ctx, rowId=None):
        if not rowId:
            return await ctx.send('Please include the id of the reminder to forget.')

        guildId = ctx.guild.id if ctx.guild else None

        try:
            responseMsg = reminders.unset_reminder(rowId, ctx.message.author.id, guildId)
            await ctx.send(responseMsg)
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        # Get all active tasks
        tasks = reminders.check_for_triggered_reminders()

        for task in tasks:
            userId = task['UserId']
            createdAt = task['CreatedAt']
            msg = task['RemindMsg']
            rowId = task['rowid']
            channelId = task['ChannelId']
            channel = self.bot.get_channel(channelId)
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

    @tasks.loop(minutes=10)
    async def channel_time(self):
        datestring = nomic_time.get_formatted_date_string()
        log.info(f'Updating channel time to {datestring}')
        channel = await self.bot.fetch_channel(config.UTC_UPDATE_CHANNEL)
        await channel.edit(name=datestring)

    @channel_time.before_loop
    async def before_channel_time(self):
        seconds_to_start = nomic_time.seconds_to_next_10_minute_increment()
        log.info(f'Seconds to start tracking time: {seconds_to_start}')
        await asyncio.sleep(seconds_to_start)


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


async def setup(bot):
    await bot.add_cog(Reminders(bot))
