import asyncio
from discord import Message
from discord.ext import commands, tasks

from config import config

from core import language, reaction_tracking
from core.utils import MemoizeCache, is_admin
from core.log import log

locale = language.Locale('cogs.vote_tracking')


class VoteTracking(commands.Cog, name='Vote Tracking'):
    '''
    A collection of commands for tracking reactions on messages.
    '''

    def __init__(self, bot) -> None:
        self.bot = bot
        self.cache = MemoizeCache(bot)

        # Holds a list of message ids that should be updated on the next scheduled update
        self.messageQueue = {}

        self.update_tracker_messages.start()

    #####################################
    # Automatic Reaction Tracking Tasks #
    #####################################
    @commands.Cog.listener('on_raw_reaction_add')
    async def on_reaction_add(self, event):
        channel = await self.cache.get_channel(event.channel_id)
        message = await self.cache.get_message(channel, event.message_id)
        created_at = message.created_at
        user = await self.cache.get_user(event.user_id)
        username = user.name

        emoji = reaction_tracking.format_emoji(event.emoji)

        reaction_tracking.add_reaction(
            event.channel_id, event.message_id, created_at, event.user_id, username, emoji)

        # Queue the message for update
        self.append_message_queue(message)

    @commands.Cog.listener('on_raw_reaction_remove')
    async def on_reaction_remove(self, event):
        channel = await self.cache.get_channel(event.channel_id)
        message = await self.cache.get_message(channel, event.message_id)
        created_at = message.created_at
        user = await self.cache.get_user(event.user_id)
        username = user.name

        emoji = reaction_tracking.format_emoji(event.emoji)

        reaction_tracking.remove_reaction(
            event.channel_id, event.message_id, created_at, event.user_id, username, emoji)

        # Queue the message for update
        self.append_message_queue(message)

    @tasks.loop(seconds=config.MESSAGE_QUEUE_UPDATE_INTERVAL)
    async def update_tracker_messages(self):
        if len(self.messageQueue) == 0:
            return

        # Run an update on every message in the dictionary and pop them as we go
        tasks = []
        for id, message in self.messageQueue.items():
            tasks.append(self.update_and_pop_message(id, message))

        asyncio.gather(*tasks)

    def append_message_queue(self, message: Message):
        if message.id not in self.messageQueue:
            self.messageQueue[message.id] = message

    async def update_and_pop_message(self, key: int, message: Message):
        await reaction_tracking.update_tracking_channels(self.cache, message)

        self.messageQueue.pop(key)

    #################
    # User Commands #
    #################
    @commands.command(
        brief='Track message reactions',
        help=('Track the reactions to messages in the given channel.\n'
              'Reaction history will be tracked for the target channel.\n'
              'That history will then be logged in this channel.\n'
              'For example, run this command in a channel called #vote-tracking,\n'
              f'The syntax for the command would be `{config.PREFIX}votetrack #proposals`.'))
    async def votetrack(self, ctx, channel=None):
        # Excuse me, do you have your key card?
        if not is_admin(ctx.author.id, ctx.guild.id):
            return ctx.send(locale.get_string('trackChannelNotAdmin'))

        # Parse to ensure that the target channel exists
        if channel is None:
            return await ctx.send(locale.get_string('trackChannelNotGiven'))

        if not channel.startswith('<#'):
            return await ctx.send(locale.get_string('trackChannelNotFormatted'))

        try:
            textChannel = await commands.TextChannelConverter().convert(ctx, channel)
        except commands.errors.ChannelNotFound:
            return await ctx.send(locale.get_string('trackChannelNotFound'))

        if not textChannel.permissions_for(textChannel.guild.me).view_channel:
            return await ctx.send(locale.get_string('trackChannelNotPermitted'))

        # Create tracking hookup for the channel
        # TODO: Add flow for tracking a limited number of reactions instead of all of them
        log.info(f'Creating new tracking relationship between #{ctx.channel.name} and #{textChannel.name}')
        result = reaction_tracking.create_channel_tracking_relationship(ctx.channel.id, textChannel.id)

        await ctx.send(result)


async def setup(bot):
    await bot.add_cog(VoteTracking(bot))
