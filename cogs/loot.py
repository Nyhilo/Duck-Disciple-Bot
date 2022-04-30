from discord.ext import commands

from core.log import log
import config.config as config
import core.loot_tables as loot
from config.config import PREFIX


class Loot(commands.Cog, name='Pools/Loot Tables'):
    '''
    A collection of commands related to weighted loot/grab tables.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Pull from weighted pools of options',
        help=('Pull an <amount> of options from a specified pool. '
              'Results are not removed between pulls when pulling multiple options.\n\n'
              'This command supports the following options:\n'
              '  pool list\n'
              '    List avaialable pools you can pull from.\n\n'
              '  pool info <poolName>\n'
              '    Get a description of the entries in a given pool.\n\n'
              '  pool roll <poolName> [amount]\n'
              '    Pull a random entry from the given pool, with an optional [amount], limit 20.\n\n'

              '  pool roll <poolName> <extraAmount> <"Extra Result"> <amount>\n'
              '    Add a number of temporary entries before pulling.\n\n'
              '  pool roll <poolName> <extraAmount> <"Extra Result"> <extraAmount 2> '
              '<"Extra Restult 2"> [...] <amount>\n'
              '    Any number of unique additional entries are allowed.\n\n'

              '  pool create <poolName>\n'
              '    Create a new pool in the current server.\n\n'
              '  pool create <poolName> global\n'
              '    Create a new global pool visible in all servers. Only usable by admins.\n\n'
              '  pool delete <poolName>\n'
              '    Delete a pool. Can only be deleted by the original author or an admin.\n\n'

              '  pool add <poolName> <"Result"> <amount>\n'
              '    Add a number of result entries to a given pool\n\n'
              '  pool remove <poolName> <"Result"> <amount>\n'
              '    Remove entries from a result. Deletes the result if it drops below 0.\n')
    )
    async def pool(self, ctx, command=None, pool=None, *args):
        if command is None:
            return ctx.send(f'Please provide an argument. See {config.PREFIX}help pool for details.')

        try:
            await self.handle_pool(ctx, command, pool, *args)
        except Exception as e:
            log.exception(e)
            await ctx.send(config.GENERIC_ERROR)

    async def handle_pool(self, ctx, comm, pool, *args):
        comm = comm.lower()
        guildId = ctx.guild.id if ctx.guild else 0
        authorId = ctx.message.author.id

        if comm == 'list':
            if pool is not None:
                return await ctx.send('The `list` command does not take any additional arguments.')

            await ctx.send(loot.list(guildId))

        if comm == 'info':
            if len(args) > 0:
                return await ctx.send('The `info` command only takes a pool name as an argument. '
                                      f'See `{PREFIX}help pool` for more info.')

            if pool is None:
                await ctx.send(loot.list(guildId))
            else:
                await ctx.send(loot.info(guildId, pool))

        if comm == 'roll':
            if pool is None:
                return await ctx.send('Please specify the name of the pool you wish operate on.')

            extraEntries, numRolls, errorMsg = parse_arbitrary_options(*args)

            if errorMsg is not None:
                return await ctx.send(errorMsg)

            if numRolls is None:
                numRolls = 1

            if numRolls > 20:
                return await ctx.send('Pulling from pools is limited to 20 pulls.')

            # TODO: This won't be neccessary after completion of this feature
            if extraEntries is None:
                extraEntries = [{'result': None, 'amount': None}]

            pages = loot.roll(guildId, pool, numRolls, extraEntries[0]['result'], extraEntries[0]['amount'])

            if type(pages) != list:
                return await ctx.send(pages)

            for page in pages:
                await ctx.send(page)

        if comm == 'create':
            if len(args) > 1:
                return await ctx.send('The `info` command a pool name and an optional (global) flag as arguments. '
                                      f'See `{PREFIX}help pool` for more info.')

            if pool is None:
                return await ctx.send('Please specify the name of the pool you wish operate on.')

            if len(pool) > 100:
                return await ctx.send('Please limit pool names to 100 characters.')

            isGlobal = len(args) < 0 and args[0].lower() == 'global'
            await ctx.send(loot.create(guildId, authorId, pool, isGlobal))

        if comm == 'delete':
            if len(args) > 0:
                return await ctx.send('The `info` command only takes a pool name as an argument. '
                                      f'See `{PREFIX}help pool` for more info.')

            await ctx.send(loot.delete(pool, guildId, authorId))

        if comm == 'add':
            resultDesc = args[0]
            amount = args[1]

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

            resultDesc = args[0]
            amount = args[1]

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


def parse_arbitrary_options(*args):
    '''
    This expects a list of integer-string pairs, with an optional final integer.
    For example: (5 "option 1" 6 "option 2" 10 "option 3" 15)

    Returns three packaged values, (argumentPairList, optionalTailInt, optionalError)
    Any of these may be None when recieved.
    '''

    # The list could just be empty...
    if len(args) == 0:
        return (None, None, None)

    # There is potentially a valid tail argument if the length of the list is odd
    # This tail could also possibly be the only argument, which is vali as well
    tail = args[-1] if len(args) % 2 == 1 else None

    # If there is a tail, it is expected to be a positive integer
    if tail is not None:
        try:
            tail = int(tail)
            if tail < 1:
                raise RuntimeError
        except ValueError:
            return (None, None, 'The number of rolls and extra entries should be integers.')
        except RuntimeError:
            return (None, None, 'The number of rolls and extra entries should be positive integers.')

    # If the tail is our only arg, then we're good to go
    if len(args) == 1:
        return (None, tail, None)

    # If there are other arguments, every even argument is expected to be an integer amount,
    # and every odd amount is expected to be a string (keeping in mind that we're 0-indexed)
    # And of course we trim off the tail if it exists
    int_args = list(args[0::2] if len(args) % 2 == 0 else args[:-1][0::2])
    string_args = list(args[1::2])

    # Just like above, all integer arguments should be positive integers
    try:
        print(int_args)
        for i, value in enumerate(int_args):
            int_args[i] = int(value)
            if int_args[i] < 0:
                raise RuntimeError
    except ValueError:
        return (None, None, 'The number of rolls and extra entries should be integers.')
    except RuntimeError:
        return (None, None, 'The number of rolls and extra entries should be positive integers.')

    # int_args and string_args are expected to be the same length, since the are derived from an even-number of elements
    return ([{'result': string_args[i], 'amount': int_args[i]} for i, _ in enumerate(int_args)], tail, None)


def setup(bot):
    bot.add_cog(Loot(bot))
