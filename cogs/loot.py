from discord.ext import commands

from core.log import log
import config.config as config
import core.loot_tables as loot
from core.db.models.pool_models import Entry
from config.config import PREFIX

import core.language as language

locale = language.Locale('cogs.pool')
globalLocale = language.Locale('global')


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

              '  pool add <poolName> <amount> <"Result">\n'
              '    Add a number of result entries to a given pool.\n\n'
              '  pool remove <poolName> <amount> <"Result">\n'
              '    Remove entries from a result. Deletes the result if it drops below 0.\n\n'
              '  pool [add/remove] <poolName> <"Result 1"> <amount 1> <"Result 2"> <amount 2> [...]\n'
              '    Multiple entries can be added or removed from a pool at a time.')
    )
    async def pool(self, ctx, command=None, pool=None, *args):
        if command is None:
            return ctx.send(locale.get_string('poolCommandNotFound', prefix=PREFIX))

        try:
            await self.handle_pool(ctx, command, pool, *args)
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    async def handle_pool(self, ctx, comm, pool, *args):
        comm = comm.lower()
        guildId = ctx.guild.id if ctx.guild else 0
        authorId = ctx.message.author.id

        if comm == 'list':
            if pool is not None:
                return await ctx.send(locale.get_string('listTooManyArgs'))

            await ctx.send(loot.list(guildId))

        if comm == 'info':
            if len(args) > 0:
                return await ctx.send(locale.get_string('infoTooManyArgs') + locale.get_string('seeHelpForInfo'))

            if pool is None:
                await ctx.send(loot.list(guildId))
            else:
                await ctx.send(loot.info(guildId, pool))

        if comm == 'roll':
            if pool is None:
                return await ctx.send(locale.get_string('rollNameNotGiven'))

            extraEntries, numRolls, errorMsg = parse_arbitrary_options(*args)

            if errorMsg is not None:
                return await ctx.send(errorMsg)

            if numRolls is None:
                numRolls = 1

            if numRolls > 20:
                return await ctx.send(locale.get_string('rollTooManyPulls'))

            pages = loot.roll(guildId, pool, numRolls, extraEntries)

            if type(pages) != list:
                return await ctx.send(pages)

            for page in pages:
                await ctx.send(page)

        if comm == 'create':
            if len(args) > 1:
                return await ctx.send(locale.get_string('createTooManyArgs') + locale.get_string('seeHelpForInfo'))

            if pool is None:
                return await ctx.send(locale.get_string('createPoolNotGiven'))

            if len(pool) > 100:
                return await ctx.send(locale.get_string('createNameTooLong'))

            isGlobal = len(args) > 0 and args[0].lower() == 'global'
            await ctx.send(loot.create(guildId, authorId, pool, isGlobal))

        if comm == 'delete':
            if len(args) > 0:
                return await ctx.send(locale.get_string('deleteTooManyArgs') + locale.get_string('seeHelpForInfo'))

            await ctx.send(loot.delete(pool, guildId, authorId))

        if comm == 'add':
            if pool is None:
                return await ctx.send(locale.get_string('addPoolNotGiven'))

            if len(args) == 0:
                return await ctx.send(locale.get_string('addResultNotGiven'))

            # If just a description is given, we just add one Entry of that result to the pool
            entries = [Entry(description=args[0])]
            if len(args) > 1:
                entries, tail, error = parse_arbitrary_options(*args)

                if tail is not None:
                    return await ctx.send(locale.get_string('addAdditionsBadFormat') + locale.get_string('seeHelpForInfo'))

                if error is not None:
                    return await ctx.send(error)

            descriptionLengths = [len(entry.description) for entry in entries]
            if max(descriptionLengths) > 1000:
                return await ctx.send(locale.get_string('addResultTooLong'))

            amounts = [entry.amount for entry in entries]
            if max(amounts) > 1000:
                return await ctx.send(locale.get_string('addTooManyResults'))

            await ctx.send(loot.add(guildId, pool, entries))

        if comm == 'remove':
            if pool is None:
                return await ctx.send(locale.get_string('removePoolNotGiven'))

            if len(args) == 0:
                return await ctx.send(locale.get_string('removeResultNotGiven'))

            # If just a description is given, we just remove one Entry of that result to the pool
            entries = [Entry(description=args[0])]
            if len(args) > 1:
                entries, tail, error = parse_arbitrary_options(*args)

                if tail is not None:
                    return await ctx.send(locale.get_string('removeAdditionsBadFormat') + locale.get_string('seeHelpForInfo'))

                if error is not None:
                    return await ctx.send(error)

            amounts = [entry.amount for entry in entries]
            if max(amounts) > 1000:
                return await ctx.send(locale.get_string('removeTooManyResults'))

            await ctx.send(loot.add(guildId, pool, entries, deleteMode=True))


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
            return (None, None, locale.get_string('errorNotIntegers') + locale.get_string('seeHelpForInfo'))

        except RuntimeError:
            return (None, None, locale.get_string('errorNotPositive') + locale.get_string('seeHelpForInfo'))

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
        for i, value in enumerate(int_args):
            int_args[i] = int(value)
            if int_args[i] < 0:
                raise RuntimeError
    except ValueError:
        return (None, None, locale.get_string('errorNotIntegers') + locale.get_string('seeHelpForInfo'))

    except RuntimeError:
        return (None, None, locale.get_string('errorNotPositive') + locale.get_string('seeHelpForInfo'))

    # int_args and string_args are expected to be the same length, since the are derived from an even-number of elements
    return ([Entry(amount=int_args[i], description=string_args[i]) for i, _ in enumerate(int_args)], tail, None)


async def setup(bot):
    await bot.add_cog(Loot(bot))
