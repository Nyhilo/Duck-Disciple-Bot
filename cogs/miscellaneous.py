import discord
from discord.ext import commands

import config.config as config

from core.log import log
import core.nomic_time as nomic_time
import core.sha as shalib
import core.utils as utils
import core.stopdoing as stopdoing


class Misc(commands.Cog, name='Miscellaneous'):
    '''
    A collection of utility commands that don't really fit in other categories.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Gets the SHA256 for a given input',
        help=('Gets the SHA256 hash for a given input. Note that including '
              'discord mentions may produce unexpected results.\n'
              'Inputs may be surrounded by double quotes to ensure expected '
              'whitespace.')
    )
    async def sha(self, ctx, *, message=None):
        if message is None:
            await ctx.send("Please include the message you would like me to hash.")
            return

        try:
            filteredMessage = utils.trim_quotes(message)
            hash = shalib.get_sha_256(filteredMessage)
            await ctx.send(f'The hash for the above message is:\n{hash}')
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)

    @commands.command(brief='Stop doing nomic', help='Stop doing it.', aliases=['stop', 'stahp'])
    async def stopdoingnomic(self, ctx):
        await stopdoing.choose(ctx, self.bot)

    @commands.Cog.listener('on_message')
    async def stopdoingnomic_inline(self, message):
        # Don't ever reply to bots
        if message.author.bot:
            return

        if 'stop doing nomic' in message.content.lower():
            await stopdoing.choose(message.channel, self.bot)

    @commands.command(
        brief='Draw a number of cards',
        help=('Automatically roll some dice and report back the dice rolls and '
              'the cards generated from those dice rolls. Will return 1 set of 1 '
              'card by default. First argument is number of cards, second argument '
              'is size of card sets. Maximum draw is 100.\n')
    )
    async def draw(self, ctx, number=1, size=1):
        if number * size < 1:
            return await ctx.send('Positive integers only please.')

        maxcards = 50
        if number * size > maxcards:
            return await ctx.send('Sorry, maximum number of cards per draw '
                                  f'is {maxcards}.')

        try:
            await ctx.send(('Here are your cards!' if number * size > 1 else 'Here is your card!'))
            await ctx.send(utils.draw_random_card_sets(number, size))
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)

    @commands.command(
        brief='Get unix timestamp for date string',
        help=('Literally just runs the given string against the python-dateutil library. '
              'Can generally be as vague or specific as you want.')
    )
    async def timestamp(self, ctx, *, message=None):
        try:
            timestamp = nomic_time.get_datestring_timestamp(message)
        except Exception:
            return await ctx.send('Whoops, I did\'t recognize the date format you sent. Try something else.')

        await ctx.send(f'Here is your timestamp for <t:{timestamp}> your time: `{timestamp}`')


async def setup(bot):
    await bot.add_cog(Misc(bot))
