import discord
from discord.ext import commands, tasks
import asyncio
import re

import config.config as config

from core.log import log
import core.reminders as reminders
import core.nomic_time as nomic_time

import core.language as language

locale = language.Locale('cogs.reminders')
globalLocale = language.Locale('global')


class Reminders(commands.Cog, name='Reminders'):
    '''
    A collection of commands related to setting reminders.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

        self.channel_time_once.start()
        self.channel_time.start()

        self.channel_phase_once.start()
        self.channel_phase.start()

        self.channel_phase_end_once.start()
        self.channel_phase_end.start()

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
            return await ctx.send(locale.get_string('helpMessage', prefix=config.PREFIX))

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
            return await ctx.send(locale.get_string('forgetIdNotGiven'))

        guildId = ctx.guild.id if ctx.guild else None

        try:
            responseMsg = reminders.unset_reminder(rowId, ctx.message.author.id, guildId)
            await ctx.send(responseMsg)
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))


    @tasks.loop(minutes=1)
    async def check_reminders(self):
        # Get all active tasks
        tasks = reminders.check_for_triggered_reminders()

        for task in tasks:
            userAt = f"<@!{task['UserId']}>"
            createdAt = f"<t:{task['CreatedAt']}:R>"
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

            _msg = f'"{msg}"' if msg else ''
            try:
                replyTo = await channel.fetch_message(task['MessageId'])
                await replyTo.reply(locale.get_string('remindFound', userAt=userAt, message=_msg))

            except discord.NotFound:
                await replyTo.reply(locale.get_string('remindChannelNotFound',
                                                      userAt=userAt, createdAt=createdAt, message=_msg))

            log.info(reminders.unset_reminder(rowId, overrideId=True))

    @tasks.loop(count=1)
    async def channel_time_once(self):
        '''Run channel_phase immediately on start before starting the actual loop'''
        return await self.channel_time()

    @tasks.loop(minutes=10)
    async def channel_time(self):
        '''
        Sets a datestring as the name of a specific configured voice channel.
        '''
        # Get the current datetime string
        datestring = nomic_time.get_formatted_date_string()

        # Update the channel name
        channel = await self.bot.fetch_channel(config.UTC_UPDATE_CHANNEL)
        await channel.edit(name=datestring)

    @channel_time.before_loop
    async def before_channel_time(self):
        '''
        Delays the start of the time tracking loop until we get to the next 10-minute increment
        '''
        seconds_to_start = nomic_time.seconds_to_next_10_minute_increment()
        log.info(f'Seconds to start tracking time: {seconds_to_start}')
        await asyncio.sleep(seconds_to_start)

    @tasks.loop(count=1)
    async def channel_phase_once(self):
        '''Run channel_phase immediately on start before starting the actual loop'''
        return await self.channel_phase()

    @tasks.loop(hours=24)
    async def channel_phase(self):
        '''
        Sets the current phase as the name of a specific configured voice channel.
        '''
        # Get the current phase string
        phasestring = nomic_time.get_current_phase_string()

        # Update the channel name
        channel = await self.bot.fetch_channel(config.PHASE_UPDATE_CHANNEL)
        await channel.edit(name=phasestring)

    @channel_phase.before_loop
    async def before_channel_phase(self):
        '''
        Delays the start of the time tracking loop until the beginning of the next day
        '''
        seconds_to_start = nomic_time.seconds_to_next_day()
        log.info(f'Seconds to start tracking phase: {seconds_to_start}')
        await asyncio.sleep(seconds_to_start)

    @tasks.loop(count=1)
    async def channel_phase_end_once(self):
        '''Run channel_phase_end immediately on start before starting the actual loop'''
        return await self.channel_phase_end()

    @tasks.loop(minutes=10)
    async def channel_phase_end(self):
        '''
        Sets the time to the end of the current phase
        '''
        # Get the current string
        channel_name = nomic_time.get_next_time_to_phase_end_string()

        # Update the channel name
        channel = await self.bot.fetch_channel(config.PHASE_END_UPDATE_CHANNEL)
        await channel.edit(name=channel_name)

    @channel_phase_end.before_loop
    async def before_channel_phase_end(self):
        '''
        Delays the start of the time tracking loop until the beginning of the next day
        '''
        seconds_to_start = nomic_time.seconds_to_next_10_minute_increment()
        log.info(f'Seconds to start tracking phase end: {seconds_to_start}')
        await asyncio.sleep(seconds_to_start)


async def handle_set_reminder(ctx, userId, createdAt, messageId, channelId, remindAfter, msg):
    if remindAfter is None:
        return await ctx.send(msg)

    if remindAfter.total_seconds() < 10:
        return await ctx.send(locale.get_string('remindSetTooShort'))

    if reminders.can_quick_remind(remindAfter):
        seconds = remindAfter.total_seconds()
        secondsAgo = nomic_time.get_timestamp(createdAt)
        
        log.info(f'Performing quick remind in {seconds} seconds')

        await ctx.send(locale.get_string('remindSetShort'))
        await asyncio.sleep(remindAfter.total_seconds())

        _msg = f'"{msg}"' if msg and len(msg) < 1000 else ''
        try:
            replyTo = await ctx.fetch_message(messageId)
            return await replyTo.reply(locale.get_string('remindFoundShort', message=_msg))
        
        except discord.NotFound:
            userAt = f'<@!{userId}>'
            createdAt = f'<t:{secondsAgo}:R>'
            return await ctx.send(locale.get_string('remindChannelNotFound',
                                                      userAt=userAt, createdAt=createdAt, message=_msg))

    try:
        responseMsg = reminders.set_new_reminder(userId, messageId, channelId, createdAt, remindAfter, msg)
        log.info(responseMsg.split('\n')[0])
        await ctx.send(responseMsg)

    except Exception as e:
        log.exception(e)
        await ctx.send(globalLocale.get_string('genericError'))


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
