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
              '    List avaialable pools you can pull from.\n\n'
              '  pool info <poolName>\n'
              '    Get a description of the entries in a given pool\n\n'
              '  pool roll <poolName>\n'
              '    Pull a random entry from the given pool\n\n'
              '  pool roll <poolName> <amount>\n'
              '    Pull multiple random entries from the given pool. Limit 100.\n\n'
              '  pool roll <poolName> <amount> <"Extra Result"> <amount>\n'
              '    Add a number of temporary entries before pulling\n\n'
              '  pool create <poolName>\n'
              '    Create a new pool in the current server\n\n'
              '  pool delete <poolName>\n'
              '    Delete a pool. Can only be deleted by the original author or an admin\n\n'
              '  pool add <poolName> <"Result"> <amount>\n'
              '    Add a number of result entries to a given pool\n\n'
              '  pool remove <poolName> <"Result"> <amount>\n'
              '    Remove entries from a result. Deletes the result if it drops below 0.\n')
    )
    async def pool(self, ctx, comm=None, pool=None, arg1=None, arg2=None, arg3=None):
        try:
            await self.handle_pool(ctx, comm, pool, arg1, arg2, arg3)
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)

    async def handle_pool(self, ctx, comm, pool, arg1, arg2, arg3):
        comm = comm.lower()
        guildId = ctx.guild.id if ctx.guild else 0
        authorId = ctx.message.author.id

        if comm == 'list':
            await ctx.send(loot.list(guildId))

        if comm == 'info':
            if pool is None:
                await ctx.send(loot.list(guildId))
            else:
                await ctx.send(loot.info(guildId, pool))

        if comm == 'roll':
            if pool is None:
                return await ctx.send('Please specify the name of the pool you wish operate on.')

            numRolls = arg1
            extraEntry = arg2
            amount = arg3

            if numRolls is None:
                numRolls = 1

            if extraEntry is not None and amount is None:
                amount = 1

            try:
                numRolls = int(numRolls)

                if extraEntry is not None:
                    amount = int(amount)

            except Exception:
                return await ctx.send('The number of rolls and extra entries should be integers.')

            if numRolls < 0 or (extraEntry is not None and amount < 0):
                return await ctx.send('The number of rolls and extra entries should be positive integers.')

            if numRolls > 20:
                return await ctx.send('Pulling from pools is limited to 20 pulls.')

            async with ctx.typing():
                pages = loot.roll(guildId, pool, numRolls, extraEntry, amount)

                if type(pages) != list:
                    return await ctx.send(pages)

                for page in pages:
                    await ctx.send(page)

                return

        if comm == 'create':
            if pool is None:
                return await ctx.send('Please specify the name of the pool you wish operate on.')

            if len(pool) > 100:
                return await ctx.send('Please limit pool names to 100 characters.')

            isGlobal = arg1 is not None and arg1.lower() == 'global'
            await ctx.send(loot.create(guildId, authorId, pool, isGlobal))

        if comm == 'delete':
            await ctx.send(loot.delete(pool, guildId, authorId))

        if comm == 'add':
            resultDesc = arg1
            amount = arg2

            if pool is None:
                return await ctx.send('Please specify a pool to remove from.')

            if resultDesc is None:
                return await ctx.send('Please specify a result to remove.')

            if len(resultDesc) > 1000:
                return await ctx.send('Pleas limit result descriptions to 1000 characters')

            if amount is None:
                amount = 1

            try:
                amount = int(amount)
            except Exception:
                return await ctx.send('The last argument in the command should be a positive integer.')

            if amount < 1:
                return await ctx.send('Please send a positive integer.')

            if amount is not None and int(amount) > 1000:
                return await ctx.send('Adding entries to a result is limited to 1000 entries at a time.')

            await ctx.send(loot.add(guildId, pool, resultDesc, amount))

        if comm == 'remove':
            if pool is None:
                return await ctx.send('Please specify the name of the pool you wish operate on.')

            resultDesc = arg1
            amount = arg2

            if pool is None:
                return await ctx.send('Please specify a pool to remove from.')

            if resultDesc is None:
                return await ctx.send('Please specify a result to remove.')

            if amount is None:
                amount = 1

            try:
                amount = int(amount)
            except Exception:
                return await ctx.send('The last argument in the command should be a positive integer.')

            if amount < 0:
                return await ctx.send('Please send a positive integer.')

            await ctx.send(loot.add(guildId, pool, resultDesc, -amount))


def setup(bot):
    bot.add_cog(Loot(bot))
