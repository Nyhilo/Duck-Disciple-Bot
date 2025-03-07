import asyncio
from datetime import datetime

from discord.ext import commands, tasks

from config import config

from core import language, nomic_time
from core.log import log

locale = language.Locale('cogs.nomic')
globalLocale = language.Locale('global')


class Nomic(commands.Cog, name="Nomic"):
    '''
    A collection of commands related to running a game of nomic.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Initialize and manage a game of nomic'
    )
    async def nomic(self, ctx, action=None):
        if action is None:
            return

        action = action.lower()

        if action == 'start':
            '''
            Starts a new game of nomic.
            '''
            return

        elif action == 'import':
            '''
            Imports a markdown file into a new ruleset.
            '''
            return

    @commands.command(
        brief='Join the current game'
    )
    async def join(self, ctx):
        pass

    @commands.command(
        brief='Leave the current game (your state will be archived)'
    )
    async def leave(self, ctx):
        pass

    @commands.command(
        brief='Add a new entry to the ruleset, gamestate, or playerstate'
    )
    async def new(self, ctx, action=None, *args):
        if action is None:
            return

        action = action.lower()

        if action == 'rule':
            '''
            Adds a new rule to the current game's ruleset
            '''
            return

        elif action == 'state':
            '''
            Adds a new gamestate section
            '''
            return

        elif action == 'playerstate ':
            '''
            Adds a section to the playerstate
            '''
            return

    @commands.command(
        brief='Rename an entry in the ruleset, gamestate, or playerstate'
    )
    async def rename(self, ctx, action=None, *args):
        if action is None:
            return

        action = action.lower()

        if action == 'rule':
            '''
            Renames a rule in the current game's ruleset
            '''
            return

        elif action == 'state':
            '''
            Renames a gamestate section
            '''
            return

        elif action == 'playerstate ':
            '''
            Renames a section in the playerstate
            '''
            return

    @commands.command(
        brief='Amend an entry in the ruleset or gamestate'
    )
    async def amend(self, ctx, action=None, *args):
        if action is None:
            return

        action = action.lower()

        if action == 'rule':
            '''
            Amend a rule
            '''
            return

        elif action == 'state':
            '''
            Amend a gamestate section
            '''
            return

    @commands.command(
        brief='Lists the rules of the game'
    )
    async def rules(self, ctx):
        return await self.rule(ctx)

    @commands.command(
        brief='Gives the text of a rule'
    )
    async def rule(self, ctx, *, name=None):
        if name is None:
            '''
            Lists the rules of the game
            '''
            return

        pass

    @commands.command(
        brief='Lists the gamestate sections of the game'
    )
    async def gamestate(self, ctx):
        return await self.rule(ctx)

    @commands.command(
        brief='Gives the text of a gamestate section'
    )
    async def state(self, ctx, *, name=None):
        if name is None:
            '''
            Lists the gamestate sections of the game
            '''
            return

        pass

    @commands.command(
        brief='Lists the current players'
    )
    async def players(self, ctx):
        return self.player(ctx)

    @commands.command(
        brief='Gives or updates the gamestate of a player'
    )
    async def player(self, ctx, playerstate=None, *, action=None):
        if playerstate is None:
            '''
            Lists the current players
            '''
            return

        (playername, section) = playerstate.split('.')

        if action is None:
            '''
            Gives the contents of a player state
            '''

        pass

    @commands.command(
        brief='Gives the history for everything, a rule, a gamestate, etc'
    )
    async def history(self, ctx):
        pass

    @tasks.loop(hours=24)
    async def create_end_of_day_archive(self):
        '''
        If needed, generate an end-of-day ruleset, gamestate, playerstate, and
        summary of changes and send them to a configured archive channel.
        '''
        pass

    @create_end_of_day_archive.before_loop
    async def before_create_end_of_day_archive(self):
        '''
        Delays the start of archive tracking until the end of the day
        '''
        seconds_to_start = nomic_time.seconds_to_next_day()
        log.info(f'Seconds to start archive loop: {seconds_to_start}')
        await asyncio.sleep(seconds_to_start)


async def setup(bot):
    await bot.add_cog(Nomic(bot))
