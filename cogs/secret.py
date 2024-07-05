import discord  # noqa F401
from discord.ext import commands

from core.log import log
from core import utils, secret_keeping

import core.language as language
locale = language.Locale('cogs.secret')
globalLocale = language.Locale('global')


class Secret(commands.Cog, name='Keeping Secrets'):
    '''
    Commands more specifically related to using hashes to perform secret actions.
    '''

    def __init(self, bot):
        self.bot = bot

    @commands.command(
        brief='Hashes a message and returns it for reference',
        help=('Similiar to the "sha"" command, this will get the SHA256 hash\n'
              'for the text sent. In addition, it will return the hashed \n'
              'string and the hash for clear reference.\n'
              'Discord mentions may produce unexpected results. Inputs may\n'
              'be surrounded by double quotes to ensure expected whitespace.')
    )
    async def secret(
        self, ctx, *,
        message=commands.parameter(description='Message to keep secret or other command', default=None)
    ):
        if message is None:
            return await ctx.send(locale.get_string('secretNone'))

        try:
            pages = utils.page_message(
                secret_keeping.format_secret_reply(message)
            )
            for page in pages:
                await ctx.send(page)

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))


async def setup(bot):
    await bot.add_cog(Secret(bot))
