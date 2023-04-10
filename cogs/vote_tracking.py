import discord
from discord.ext import commands, tasks

from config import config

from core import language, log

locale = language.Locale('cogs.vote_tracking')


class VoteTracking(commands.Cog, name='Vote Tracking'):
    '''
    A collection of commands for tracking reactions on messages.
    '''

    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.Cog.listener('on_raw_reaction_add')
    async def on_reaction_add(self, event):
        message_id, user_id, member, emoji = event.message_id, event.user_id, event.member, event.emoji

        for p in [message_id, user_id, member, emoji]:
            print(f'{p=}')

    @commands.Cog.listener('on_raw_reaction_remove')
    async def on_reaction_remove(self, event):
        message_id, user_id, member, emoji = event.message_id, event.user_id, event.member, event.emoji

        for p in [message_id, user_id, member, emoji]:
            print(f'{p=}')



async def setup(bot):
    await bot.add_cog(VoteTracking(bot))
