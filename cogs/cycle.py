import discord  # noqa F401
from discord.ext import commands, tasks
import asyncio
import contextlib
from dateutil.parser import ParserError

from core.log import log
from core import nomic_time
from config import config
from config.settings import settings

import core.language as language

globalLocale = language.Locale('global')


class Cycle(commands.Cog, name='Current Cycle'):
    '''
    Commands related to the current Cycle of Infinite Nomic.
    '''

    def __init__(self, bot):
        self.bot = bot

        self.update_khronos.start()

        self.channel_time.start()
        self.channel_phase.start()
        self.channel_phase_end.start()

    @commands.command(
        brief='Get information about the time relevant to the current Cycle',
        help=('Get current time and day in UTC, as well asn any relevant '
              'information regarding time in the current Cycle')
    )
    async def time(self, ctx):
        try:
            await ctx.send(nomic_time.get_current_utc_string())
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    ###########
    # Khronos #
    ###########
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

    @tasks.loop(count=1)
    async def update_khronos(self):
        '''Run time trackers immediately on start before starting the actual loop'''
        await self.channel_time()
        await self.channel_phase()
        await self.channel_phase_end()

    ##################
    # Cycle Commands #
    ##################
    @commands.command(
        brief='Starts a new cycle',
        help=('Triggers Khronos to begin tracking a new cycle on the current '
              'date. It will use the phase loop pattern of the previous cycle. '
              'Use setphaseloop to update the loop pattern')
    )
    async def cycleinfo(self, ctx):
        try:
            await ctx.send(
                f'Cycle currently running?: **{settings.cycle_running}**\n'
                f'Cycle start date: **{settings.current_cycle_start_date.strftime("%Y-%m-%d")}**\n'
                f'Configured phase loop: **{" -> ".join(str(v) for v in settings.current_cycle_phase_loop)}**\n'
                f'Configured phase names: **{" -> ".join(settings.current_cycle_phase_names)}**'
            )

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    @commands.command(
        brief='Starts a new cycle',
        help=('Triggers Khronos to begin tracking a new cycle on the current '
              'date. It will use the phase loop pattern of the previous cycle. '
              'Use setphaseloop to update the loop pattern')
    )
    async def startcycle(self, ctx):
        try:
            if settings.cycle_running:
                return await ctx.send('A cycle is currently running!')

            settings.current_cycle_start_date = nomic_time.utc_now()
            nomic_time.set_locale('core.nomic_time')
            settings.cycle_running = True

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

        try:
            notify_task = asyncio.create_task(self.notify_rate_limit(ctx))
            await self.update_khronos()
        finally:
            notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await notify_task

        await ctx.send("A new Cycle has started. Have fun!")

    @commands.command(
        brief='Ends the current cycle',
        help=('Triggers Khronos to display the between-cycle messages')
    )
    async def endcycle(self, ctx):
        try:
            if not settings.cycle_running:
                return await ctx.send('A cycle is not currently running!')

            settings.cycle_running = False
            nomic_time.set_locale('core.nomic_time_on_break')

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

        try:
            notify_task = asyncio.create_task(self.notify_rate_limit(ctx))
            await self.update_khronos()
        finally:
            notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await notify_task

        await ctx.send("Cycle has ended. See you next time!")

    @commands.command(
        brief='Sets the start date for the current cycle',
        help=('This is used to calculate the week and phase number.\n'
              'Determines the date using the python date parser, but it is '
              'suggested to use a date format that is unambiguous')
    )
    async def setstartdate(self, ctx, datestring):
        try:
            startDate = nomic_time.get_datestring_datetime(datestring)
            settings.current_cycle_start_date = startDate

        except ParserError:
            await ctx.send('You did not provide a valid date format. '
                           'Try YYYY-MM-dd')

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

        try:
            notify_task = asyncio.create_task(self.notify_rate_limit(ctx))
            await self.update_khronos()
        finally:
            notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await notify_task

        await ctx.send(f'Updated start date to {settings.current_cycle_start_date.strftime("%Y-%m-%d")}')

    @commands.command(
        brief='Set the pattern for the phase loop this cycle',
        help=('Provide a list of numbers. I.e &setphaseloop 3 2 2'
              'Defines the loop in which phases are caluculated starting with '
              'the start date.\n'
              'For instance, a cycle of [3, 2, 2] would have a 3-day Phase I, '
              '2-day Phase II, and a 2-day Phase III.\n'
              'Khrono defines a "week" as the sum of all parts of the phase, '
              'so consider ensuring that they add up to 7.')
    )
    async def setphaseloop(self, ctx, *args):
        try:
            if len(args) < 1:
                return await ctx.send("You must send a list of integrers")

            settings.current_cycle_phase_loop = list(args)

        except ValueError:
            await ctx.send('You must send a list of integers')

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

        try:
            notify_task = asyncio.create_task(self.notify_rate_limit(ctx))
            await self.update_khronos()
        finally:
            notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await notify_task

        await ctx.send(f'Updated phase loop to {" -> ".join(str(v) for v in settings.current_cycle_phase_loop)}')

    @commands.command(
        brief='Set the pattern for the phase loop this cycle',
        help=('Provide a list of names. These can be space OR comma separated, '
              'but names with spaces should be in quotes.'
              'Defines the names of each phase in the phase loop.'
              'If the number of phases is larger than the number of names, '
              'Khronos will use the final name for all the end phases.')
    )
    async def setphasenames(self, ctx, *args):
        try:
            if len(args) < 1:
                return await ctx.send("You must send a list of names")

            settings.current_cycle_phase_names = list(args)

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

        try:
            notify_task = asyncio.create_task(self.notify_rate_limit(ctx))
            await self.update_khronos()
        finally:
            notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await notify_task

        await ctx.send(f'Updated phase names to {" -> ".join(settings.current_cycle_phase_names)}')

    async def notify_rate_limit(self, ctx):
        await asyncio.sleep(3)
        await ctx.send(globalLocale.get_string('rateLimitMessage'))


async def setup(bot):
    await bot.add_cog(Cycle(bot))
