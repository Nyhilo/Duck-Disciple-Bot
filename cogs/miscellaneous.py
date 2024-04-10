import discord  # noqa: F401
from discord.ext import commands

from core.log import log
from core import nomic_time, sha as shalib, utils, stopdoing, language, prospecting
from config.config import STOP_DOING_ONMESSAGE_GUILD_WHITELIST

locale = language.Locale('cogs.misc')
globalLocale = language.Locale('global')


class Misc(commands.Cog, name='Miscellaneous'):
    '''
    A collection of utility commands that don't really fit in other categories.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.stopdoing = stopdoing.StopDoing(bot)

    @commands.command(
        brief='Gets the SHA256 for a given input',
        help=('Gets the SHA256 hash for a given input. Note that including '
              'discord mentions may produce unexpected results.\n'
              'Inputs may be surrounded by double quotes to ensure expected '
              'whitespace.')
    )
    async def sha(self, ctx, *, message=None):
        if message is None:
            await ctx.send(locale.get_string('shaInputMissing'))
            return

        try:
            filteredMessage = utils.trim_quotes(message)
            hash = shalib.get_sha_256(filteredMessage)
            await ctx.send(locale.get_string('shaHashGiven', hash=hash))
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    @commands.command(brief='Stop doing nomic', help='Stop doing it.', aliases=['stop', 'stahp'])
    async def stopdoingnomic(self, ctx):
        await self.stopdoing.choose(ctx, None, True)

    @commands.Cog.listener('on_message')
    async def stopdoingnomic_inline(self, message):
        # Don't ever reply to bots
        if message.author.bot:
            return

        if message.guild.id not in STOP_DOING_ONMESSAGE_GUILD_WHITELIST:
            return

        await self.stopdoing.choose(message.channel, message.content)

    @commands.command(
        brief='Draw a number of cards',
        help=('Automatically roll some dice and report back the dice rolls and '
              'the cards generated from those dice rolls. Will return 1 set of 1 '
              'card by default. First argument is number of cards, second argument '
              'is size of card sets. Maximum draw is 100.\n')
    )
    async def draw(self, ctx, number=1, size=1):
        if number * size < 1:
            return await ctx.send(locale.get_string('cardsNotPositive'))

        maxcards = 50
        if number * size > maxcards:
            return await ctx.send(locale.get_string('cardTooMany', maxcards=maxcards))

        try:
            if number * size > 1:
                await ctx.send(locale.get_string('cardSuccessPlural'))
            else:
                await ctx.send(locale.get_string('cardSuccess'))

            await ctx.send(utils.draw_random_card_sets(number, size))
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    @commands.command(
        brief='Get unix timestamp for date string',
        help=('Literally just runs the given string against the python-dateutil library. '
              'Can generally be as vague or specific as you want.')
    )
    async def timestamp(self, ctx, *, message=None):
        try:
            timestamp = nomic_time.get_datestring_timestamp(message)
            formattedTimestamp = f'<t:{timestamp}>'
        except Exception:
            return await ctx.send(locale.get_string('timestampBadFormat'))

        await ctx.send(locale.get_string('timestampSuccess',
                                         formattedTimestamp=formattedTimestamp,
                                         timestamp=timestamp))

    @commands.command(
        brief='Play the Prospecting demo minigame'
    )
    async def prospect(self, ctx):
        await prospecting.run_game(ctx, self.bot)


async def setup(bot):
    await bot.add_cog(Misc(bot))
