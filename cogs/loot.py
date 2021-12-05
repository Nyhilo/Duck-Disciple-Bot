import discord
from discord.ext import commands

from core.log import log
import config.config as config


class Loot(commands.Cog, name='Pools/Loot Tables'):
    '''
    A collection of commands related to weighted loot/grab tables.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pool(self, ctx, comm=None, table=None, arg=None, amount=None):
        await ctx.send(f'{comm=}\n{table=}\n{arg=}\n{amount=}')


def setup(bot):
    bot.add_cog(Loot(bot))
