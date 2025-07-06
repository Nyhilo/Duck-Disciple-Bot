import discord
from discord.ext import commands, tasks
import asyncio
import re

from config import config

from core import reminders, nomic_time, language
from core.log import log
from core.enums import Reoccur

locale = language.Locale('cogs.reminders')
globalLocale = language.Locale('global')


class Reminders(commands.Cog, name='Reminders'):
    '''
    A collection of commands related to setting reminders.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    @commands.command(
        brief='Have the bot remind you about something',
        help=(f'Usages: &remind [number] [second(s)|minute(s)|hour(s)|day(s)|week(s)] <message>\n'
              f'        &remind [timestamp] <message>\n'
              f'        &remind [datestring]; <message>\n'
              'Will save a reminder and reply in the same channel at the specified point in the future.\n'
              'Long-term reminders are checked once per minute. Adding a message is optional, '
              'and will be echoed back to you.\n\n'
              'Escape users and roles in the creation message with a backslash on either side of the "@".\n'
              'For example, \\@\\Username and \\@\\everyone will be echoed back as @Username and @everyone.\n\n'
              'Examples:\n'
              f"\t{config.PREFIX}remind 5 days\n"
              f"\t{config.PREFIX}remind 7 days Hey \\@\\everyone it's time!\n"
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
            responseMsg = reminders.unset_reminder(
                rowId, ctx.message.author.id, guildId)
            await ctx.send(responseMsg)
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    @commands.command(
            brief='Set a reoccuring reminder',
            help=(f'Uses the same syntax as {config.PREFIX}remind.\n'
                  'Follows up for the reoccurrence interval after setting for the reminder.\n'
                  'Reoccurence intervals are as follows:\n'
                  '\tDaily: Repeats every 24 hours\n'
                  '\tBi-Daily: Repeats every 48 hours\n'
                  '\tWeekly: Repeats every 7 days\n'
                  '\tFornightly: Repeats every 14 days\n'
                  '\tMonthly: Repeats each month on the day†\n'
                  '\tMonth-End: Repeats at the end of each month'
                  '\tYearly: Repeats every year on the day†\n'
                  '\tYear-End: Repeats on the last day of the year\n'
                  '† If set on the 31st, 30th, or 29th, will repeat on the '
                  '30th, 29th, or 28th of subsequent months as needed.\n'
                  'This command also supports abbreviations, e.g. w for weekly or me for month-end.')
    )
    async def reoccur(self, ctx, *, message=None):
        if not message:
            return await ctx.send(locale.get_string('helpMessage', prefix=config.PREFIX))

        # Get Info to set
        userId = ctx.message.author.id
        createdAt = ctx.message.created_at
        messageId = ctx.message.id
        channelId = ctx.channel.id
        remindAfter, _msg = reminders.parse_remind_message(message, createdAt)
        msg = await filter_escaped_mentions(ctx, _msg)

        validIntResponses = {
            '1': 'Daily',
            '2': 'Bi-Daily',
            '3': 'Weekly',
            '4': 'Fornightly',
            '5': 'Monthly',
            '6': 'Month-end',
            '7': 'Yearly',
            '8': 'Year-end'
        }

        validStringResponses = {
            'daily': 1,
            'day': 1,
            'd': 1,
            'bi-daily': 2,
            'bidaily': 2,
            'biday': 2,
            'bd': 2,
            'weekly': 3,
            'week': 3,
            'w': 3,
            'fornightly': 4,
            'fortnight': 4,
            'fortnite': 4,
            'fn': 4,
            'monthly': 5,
            'month': 5,
            'm': 5,
            'month-end': 6,
            'monthend': 6,
            'me': 6,
            'yearly': 7,
            'year': 7,
            'y': 7,
            'year-end': 8,
            'yearend': 8,
            'ye': 8
        }

        reoccurList = ', '.join([f'{k}: {v}' for k, v in validIntResponses.items()])

        try:
            reoccurChoice = 0
            await ctx.send(locale.get_string('getReoccurrence', reoccurList=reoccurList))

            def check(m):
                if m.channel == ctx or m.channel == ctx.channel:
                    msg = m.content.lower()
                    return str(msg) in validIntResponses or msg.lower() in validStringResponses

                return False

            response = (await self.bot.wait_for('message', timeout=120, check=check)).content

            if response in validIntResponses:
                reoccurChoice = int(response)

            if response.lower() in validStringResponses:
                reoccurChoice = validStringResponses[response.lower()]

        except asyncio.TimeoutError:
            await ctx.send(locale.get_string('reoccurTimeout'))

        return await handle_set_reminder(ctx, userId, createdAt, messageId, channelId, remindAfter, msg, reoccurChoice)

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
                log.info(
                    f'Channel with id {channelId} does not exist. Setting reminder with id {rowId} to inactive...')
                if rowId:
                    unsetMsg = reminders.unset_reminder(rowId, overrideId=True)
                    log.info(unsetMsg)
                continue

            _msg = f'"{msg}"' if msg else ''
            try:
                replyTo = await channel.fetch_message(task['MessageId'])
                if task['Reoccur'] is None or task['Reoccur'] == 0:
                    await replyTo.reply(locale.get_string('remindFound', userAt=userAt, message=_msg))
                else:
                    await replyTo.reply(_msg)
                    reminders.refresh_reoccuring_reminder(task)

            except discord.NotFound:
                await replyTo.reply(locale.get_string('remindChannelNotFound',
                                                      userAt=userAt, createdAt=createdAt, message=_msg))
            if task['Reoccur'] is None or task['Reoccur'] == 0:
                log.info(reminders.unset_reminder(rowId, overrideId=True))


async def handle_set_reminder(ctx, userId, createdAt, messageId, channelId, remindAfter, msg, reoccur=Reoccur.NONE):
    if remindAfter is None:
        return await ctx.send(msg)

    if remindAfter.total_seconds() < 10:
        return await ctx.send(locale.get_string('remindSetTooShort'))

    if reoccur == Reoccur.NONE and reminders.can_quick_remind(remindAfter):
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
        responseMsg = reminders.set_new_reminder(
            userId, messageId, channelId, createdAt, remindAfter, msg, reoccur)
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

    # Find all escaped user and role mentions
    matches = re.finditer(r'\\@\\\w+(?:#\d{4})?', message)
    for m in matches:
        match = m.group()
        mention = match.replace('\\@\\', '')

        # Try to convert the mention to a user
        result = await resolve_mention(memberConverter, mention)

        # If it wasn't a username, try to convert it to a role
        if result == mention:
            result = await resolve_mention(roleConverter, mention)

        # If it wasn't a role, just put the @ sign back and call it a day
        if result == mention:
            result = '@' + mention

        message = message.replace(match, result)

    return message


async def setup(bot):
    await bot.add_cog(Reminders(bot))
