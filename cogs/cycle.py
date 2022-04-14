import discord
from discord.ext import commands

from core.log import log
import core.nomic_time as nomic_time
import config.config as config


class Cycle(commands.Cog, name='Current Cycle'):
    '''
    Commands related to the current Cycle of Infinite Nomic.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Get information about the current relevant Cycle time',
        help=('Get current time and day in UTC, as well asn any relevant '
              'cycle information')
    )
    async def time(self, ctx):
        try:
            await ctx.send(nomic_time.get_current_utc_string())
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)


def setup(bot):
    bot.add_cog(Cycle(bot))
