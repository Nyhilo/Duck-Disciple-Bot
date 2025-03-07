import discord
from discrod.ext import commands

from config import config

from core import language
from core.log import log

locale = language.Locale('cogs.nomic')
globalLocale = language.Locale('global')


class Nomic(commands.Cog, name="Nomic"):
    '''
    A collection of commands related to running a game of nomic.
    '''

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Nomic(bot))
