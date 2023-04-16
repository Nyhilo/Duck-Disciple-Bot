from discord import TextChannel, Message, User
from discord.ext import commands

from config import config

from core import language, log, reaction_tracking

locale = language.Locale('cogs.vote_tracking')


class VoteTracking(commands.Cog, name='Vote Tracking'):
    '''
    A collection of commands for tracking reactions on messages.
    '''

    def __init__(self, bot) -> None:
        self.bot = bot
        self.cachedChannels = {}
        self.cachedMessages = {}
        self.cachedUsers = {}

    @commands.Cog.listener('on_raw_reaction_add')
    async def on_reaction_add(self, event):
        channel = await self.get_channel(event.channel_id)
        message = await self.get_message(channel, event.message_id)
        created_at = message.created_at
        user = await self.get_user(event.user_id)
        username = user.name

        emoji = reaction_tracking.format_emoji(event.emoji)

        await channel.send(emoji)

        reaction_tracking.add_reaction(event.channel_id, event.message_id, created_at, event.user_id, username, emoji)

    @commands.Cog.listener('on_raw_reaction_remove')
    async def on_reaction_remove(self, event):
        message_id, user_id, member, emoji = event.message_id, event.user_id, event.member, event.emoji

        for p in [message_id, user_id, member, emoji]:
            print(f'{p=}')

    @commands.command(
        brief='Track message reactions',
        help=('Track the reactions to messages in the given channel.\n'
              'Reaction history will be tracked for the target channel.\n'
              'That history will then be logged in this channel.\n'
              'For example, run this command in a channel called #vote-tracking,\n'
              f'The syntax for the command would be `{config.PREFIX}votetrack #proposals`.'))
    async def votetrack(self, ctx, channel=None):
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

        # TODO: Add flow for tracking a limited number of reactions instead of all of them

        log.info(f'Attempting to create new tracking relationship between #{ctx.name} and #{textChannel.name}')
        result = reaction_tracking.create_channel_tracking_relationship(ctx.channel.id, textChannel.id)
        
        await ctx.send(result)

    async def get_channel(self, id: int) -> TextChannel:
        if id not in self.cachedChannels:
            print(f'Caching channel {id}')
            self.cachedChannels[id] = await self.bot.fetch_channel(id)
        else:
            print(f'Getting cached channel {id}')

        return self.cachedChannels[id]

    async def get_message(self, channel: TextChannel, id: int) -> Message:
        if id not in self.cachedMessages:
            print(f'Caching message {id}')
            self.cachedMessages[id] = await channel.fetch_message(id)
        else:
            print(f'Getting cached message {id}')

        return self.cachedMessages[id]

    async def get_user(self, id: int) -> User:
        if id not in self.cachedUsers:
            print(f'Caching user {id}')
            self.cachedUsers[id] = await self.bot.fetch_user(id)
        else:
            print(f'Getting cached user {id}')

        return self.cachedUsers[id]


async def setup(bot):
    await bot.add_cog(VoteTracking(bot))
