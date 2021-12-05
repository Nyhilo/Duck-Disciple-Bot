import discord
from discord.ext import commands

from core.log import log
import config.config as config
import core.loot_tables as loot


class Loot(commands.Cog, name='Pools/Loot Tables'):
    '''
    A collection of commands related to weighted loot/grab tables.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Pull from weighted pools of options',
        help=('This command supports the following options:\n'
              '  pool list\n'
              '    List avaialable pools you can pull from.\n'
              '  pool info <poolName>\n'
              '    Get a description of the entries in a given pool\n'
              '  pool roll <poolName>\n'
              '    Pull a random entry from the given pool\n'
              '  pool roll <poolName> <"Extra Result"> <amount>\n'
              '    Add a number of temporary entries before pulling\n'
              '  pool create <poolName>\n'
              '    Create a new pool in the current server\n'
              '  pool delete <poolName>\n'
              '    Delete a pool. Can only be deleted by the original author or an admin\n'
              '  pool add <poolName> <"Result"> <amount>\n'
              '    Add a number of result entries to a given pool\n'
              '  pool remove <poolName> <"Result"> <amount>\n'
              '    Remove entries from a result. Deletes the result if it drops below 0.\n')
    )
    async def pool(self, ctx, comm=None, pool=None, arg=None, amount=None):
        try:
            await self.handle_pool(ctx, comm, pool, arg, amount)
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)

    async def handle_pool(self, ctx, comm, pool, arg, amount):
        comm = comm.lower()
        guildId = ctx.guild.id if ctx.guild else 0
        authorId = ctx.message.author.id

        if comm == 'list':
            await ctx.send(loot.list(guildId))

        if comm == 'info':
            if pool is None:
                await ctx.send(loot.list(guildId))
            else:
                await ctx.send(loot.info(pool))

        if comm == 'roll':
            await ctx.send(loot.roll(guildId, pool, arg, amount))

        if comm == 'create':
            isGlobal = arg.lower() == 'global'
            await ctx.send(loot.create(guildId, authorId, pool, isGlobal))

        if comm == 'delete':
            await ctx.send(loot.delete(pool, guildId, authorId))

        if comm == 'add':
            await ctx.send(loot.add(guildId, pool, arg, amount))

        if comm == 'remove':
            await ctx.send(loot.add(guildId, pool, arg, -amount))


def setup(bot):
    bot.add_cog(Loot(bot))
