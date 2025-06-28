import discord  # noqa F401
from discord.ext import commands

from core.log import log
from core import nomic_time

import core.language as language
from config.settings import settings

globalLocale = language.Locale('global')


class Cycle(commands.Cog, name='Current Cycle'):
    '''
    Commands related to the current Cycle of Infinite Nomic.
    '''

    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(
        brief='Starts a new cycle',
        help=('Triggers Khronos to begin tracking a new cycle on the current '
              'date. It will use the phase loop pattern of the previous cycle. '
              'Use setphaseloop to update the loop pattern')
    )
    async def startcycle(self, ctx, name):
        try:
            settings.current_cycle_start_date = nomic_time.utc_now()
            settings.between_cycles = False
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    @commands.command(
        brief='Ends the current cycle',
        help=('Triggers Khronos to display the between-cycle messages')
    )
    async def endcycle(self, ctx):
        try:
            settings.between_cycles = True
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

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
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

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
    async def setphaseloop(self, ctx):
        try:
            pass
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))


async def setup(bot):
    await bot.add_cog(Cycle(bot))
