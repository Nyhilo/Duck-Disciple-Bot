import discord  # noqa: F401
from discord.ext import commands

from core import language

locale = language.Locale('cogs.locale')
globalLocale = language.Locale('global')


class Locale(commands.Cog, name='Locale'):
    '''
    A collection of commands related to language settings for the bot.
    '''

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def locale(self, ctx, locale_name=None):
        if locale_name is None:
            return await ctx.send(locale.get_string('setNoLocaleGiven'))

        try:
            locale.set_locale(locale_name)
        except Exception:
            return await ctx.send(locale.get_string('setLocaleNotFound'))

        return await ctx.send(locale.get_string('setLocaleSuccess', locale_name=locale_name))


async def setup(bot):
    await bot.add_cog(Locale(bot))
