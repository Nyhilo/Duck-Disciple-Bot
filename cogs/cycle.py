import discord
from discord.ext import commands

from math import ceil, sqrt

from core.log import log
import core.nomic_time as nomic_time
import config.config as config

import core.language as language
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


async def setup(bot):
    await bot.add_cog(Cycle(bot))
