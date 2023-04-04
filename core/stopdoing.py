import discord

from random import choices, random
from time import sleep
import asyncio
from typing import Callable, List, Union
import re

import config.config as config
from core.log import log

from core import language

locale = language.Locale('core.stopdoing')


class Option():
    def __init__(self, func: Callable, weight: int, extra_arg: str = None,
                 regexes: Union[str, List[str]] = None):
        """
        An option holds a delegate function so it can be executed later. It also
        allows you to pass an optional additional argument to the delegate.

        :param func:      Delegate function to be executed if this option is
                           chosen
        :param weight:    How many instances of the option are included in the
                           option pool
        :param regex:     Optional regex to match against for arbitrary message
                           replies, defaults to None
        :param extra_arg: An optional additional argument that gets passed to
                           'func' delegate, defaults to None
        """
        self.func = func
        self.weight = weight
        self.extra_arg = extra_arg

        # Let's pre-compile our regexes with case-insensitivity for use later
        if type(regexes) is str:
            regexes = [regexes]

        self.regexes = None if regexes is None else [re.compile(r, re.IGNORECASE) for r in regexes]

    async def execute(self, ctx) -> None:
        """
        Executes the delegate of this option.

        :param ctx: The discord context (usually a "messageable" object) in
                     which to execute this delegate. Used to respond to the
                     triggering message
        """
        if self.extra_arg:
            return await self.func(ctx, self.extra_arg)

        return await self.func(ctx)


class StopDoing():
    def __init__(self, bot) -> None:
        """
        Caches the bot object and options list for use.

        :param bot: _description_
        """
        self.bot = bot
        punc = r'(?:[\.!?])?'
        stop = r'(not|stop(?:ped)?)'
        nomic = rf'{stop} doing nomic'

        self.options = [
            # Classic Stop Doing Nomic
            Option(send_image, 15, 'square stop doing nomic.png', nomic),
            Option(send_image, 10, 'stop doing plantnomic.png', rf'{stop} doing (nomic|plant)'),
            Option(send_image, 15, 'stop doing cfjs.png', [nomic, rf'{stop} doing cfj']),
            Option(send_image, 15, 'trungified stop doing.png', nomic),
            Option(send_image, 15, 'absolute fools.png', r'absolute fool'),

            # Stop doing STEM
            Option(send_image, 10, 'stop doing math.png', rf'{stop} doing math'),
            Option(send_image, 2, 'start doing math.jpg', r'start doing math'),
            Option(send_image, 10, 'stop doing derivatives.jpg', rf'{stop} doing (math|derivatives|calculus)'),
            Option(send_image, 5, 'stop doing medicine.jpg', rf'{stop} doing medicine'),
            Option(send_image, 5, 'stop doing chemistry.png', rf'{stop} doing chemistry'),
            Option(send_image, 5, 'stop doing physics.png', rf'{stop} doing (?:quantum )?physics'),
            Option(send_image, 10, 'stop doing logic.jpg', rf'{stop} doing logic'),
            Option(send_image, 15, 'stop doing computer science.png',
                   rf'{stop} doing (compsci|computer science|programming|coding)'),

            # Stop doing other nerd stuff
            Option(send_image, 5, 'stop doing linguistics.png', rf'{stop} doing (linguistics|language)'),
            Option(send_image, 2, 'stop using c.png', rf'{stop} (doing|using) (linguistics|language|the letter c)'),
            Option(send_image, 5, 'stop doing nixos.png', rf'{stop} doing nixos'),
            Option(send_image, 5, 'stop doing chess.png', rf'{stop} (doing|playing) chess'),
            Option(send_image, 4, 'stop doing music.png', rf'{stop} (doing|playing) music'),
            Option(send_image, 2, 'stop doing music theory.png',
                   [rf'{stop} (doing|playing) music', rf'{stop} doing music theory']),
            Option(send_image, 5, 'stop doing keyboards.jpg',
                   rf'{stop} (doing|using) (?:mech |mechanical )?(?:key)?board'),

            # Stop doing roads
            Option(send_image, 10, 'stop driving cars.png', rf'{stop} (doing|building|driving) (cars|road)'),
            Option(send_image, 1, 'tramsgender.png', rf'{stop} (doing|building|driving) (cars|road)'),
            Option(send_image, 1, 'stop doing roads_mtg.png', rf'{stop} (doing|building|driving) (cars|road)'),

            # Other Stop doing ___
            Option(send_image, 5, 'stop digging here.png', rf'{stop} digging here'),

            # Stop Doing.
            Option(send_image, 10, 'stop doing.png', [rf'stop doing{punc}$', nomic]),
            Option(send_image, 1, 'stop doing2.jpg', [rf'stop doing{punc}$', nomic]),
            Option(send_image, 1, 'stop doing3.jpg', [rf'stop doing{punc}$', nomic]),
            Option(send_image, 10, 'stop doing stop doing.png',
                   [rf'{stop} doing (?:.)?stop doing', rf'{stop} doing{punc}$']),

            # Gif responses
            Option(send_image, 5, 'mexican hankerchief.gif', r'^kek(?:.)?$'),
            Option(send_image, 5, 'stop it get some help.gif',
                   [nomic, rf'stop doing{punc}$', r'get some help']),
            Option(send_image, 3, 'nej men hej.gif', [r'^nej men hej$', r'^nmh$']),

            # Misc Infinite Nomic memes
            Option(send_image, 10, 'you could make a nomic.png', [nomic, r'(could|can) make a nomic out of']),
            Option(send_image, 5, 'how can he do this without drowning.jpg', rf'^how can .+ do this{punc}$'),
            Option(send_image, 3, 'cool hat.jpg', r'cool.hat'),
            Option(send_image, 10, 'all the players gone.png', [r'dead (game|nomic)', nomic]),
            Option(send_image, 5, 'should.png', r'^(?:.)?should(?:.)?$'),
            Option(send_image, 5, 'reasonably.png', r'^(?:.)?reasonably(?:.)?$'),
            Option(send_image, 5, 'birb vs ml.png', rf'{stop} doing (ml|machine learning)'),

            # Misc Non-IN memes
            Option(send_image, 5, 'become unponderable.png', r'become unponderable'),
            Option(send_image, 10, 'big brain granny.png', r'big brain'),

            # Misc Emotes
            Option(thistbh, 15, None, [nomic, r'this tbh', rf'^(this|this tbh){punc}$']),
            Option(what, 8, None, r'^what(?:\.)?$'),
            Option(nylo, 8, None, rf'(?:.{{0,10}})(nylo|nyhilo){punc}$'),  # {0,10} allows for "thanks/based nylo" etc.

            # Amogi
            Option(amogus, 7, None, r'^amogus$'),
            Option(amogus2, 3, None, r'^amogus$'),
            Option(amogus3, 2, None, r'^amogus$'),
            Option(send_image, 1, 'stop posting amongus.png',
                   [r'^amogus$', rf'{stop} (doing|posting|saying) (among us|amongus|amogus|ඞ)']),

            # Rare triggers
            Option(bossy, 1, None, nomic),
            Option(downloadupdate, 2, bot, nomic)
        ]

    async def choose(self, ctx, msg: str, generic_selection: bool = False) -> None:
        """
        Select a "stop doing" meme and reply to the context with it. Will
        randomly select a result that regex matches the input message if one
        exists, or randomly selects from all options if generic_selection is
        True.

        :param ctx:               The context in which to respond to a trigger
        :param msg:               A message sent by a user that will be matched
        :param generic_selection: Indicates that we should select from all
                                   possible options and that we shouldnot bother
                                   regex-matching, defaults to False
        """
        # This is sincerity protection. Longer messages are more likely to be
        # sincere non-jokes, so we don't want to be a pest in that context
        if not generic_selection and len(msg) > config.STOP_DOING_MSG_LEN_LIMIT:
            return

        # Compile a list of options to choose from later
        options_ = self.getOptionsForInput(None if generic_selection else msg)

        if len(options_) == 0:
            return

        # We have a fixed chance of just posting the usual image
        # explicitly triggering with "stop doing nomic" also overrides the normal weight calculation
        if ((generic_selection or re.search(r'stop(?:ped)? doing nomic', msg.lower()))
                and random() < config.STOP_DOING_DEFAULT_CHANCE):
            response = config.DEFAULT_STOP_DOING_RESPONSE
            log.info('Sending default stopdoing response: {response}')
            return await send_image(ctx, response)

        # If we don't post that one, we select from the option list
        option = choices(
            options_, weights=[option.weight for option in options_])[0]
        log.info(f'Sending stopdoing response: {option.func.__name__}, "{option.extra_arg}"')

        await option.execute(ctx)


    def getOptionsForInput(self, msg: str = None) -> List[Option]:
        '''
        Returns a list of all options that match the regex for the provided msg

        :param msg: Input message
        :return:    List of matching Option objects
        '''

        if msg is None:
            return self.options

        options = []
        # Search all options that allow regex matching
        for option in [o for o in self.options if o.regexes is not None]:
            # if an option has multiple matches, any of them can make the option valid
            if any([r.search(msg) for r in option.regexes]):
                options.append(option)

        return options


def odds(msg: str = None) -> str:
    '''
    Returns a description of all option weights for a given request msg.
    Or the sum of all weights if no request msg is provided.

    :para msg: String that would trigger detection in normal usage
    '''

    stop = StopDoing(None)
    total_weights = sum([option.weight for option in stop.options])

    if msg is None:
        return f'The total weights of all options is: {total_weights}'

    filtered_options = stop.getOptionsForInput(msg)
    filtered_weights = sum([option.weight for option in filtered_options])
    return (f'Weights:    {filtered_weights}\n'
            f'Total:      {total_weights}\n'
            f'Proportion: {(filtered_weights/total_weights)*100:.2f}%')


####################
# Choice functions #
####################


async def send_image(ctx, filename):
    async with ctx.typing():
        with open(f'{config.SDN_DIR}/{filename}', 'rb') as file:
            f = discord.File(file, filename=filename)

        await ctx.send(file=f)


async def thistbh(ctx):
    await ctx.send('<:thistbh:921574440813346897>')


async def what(ctx):
    await ctx.send('<:raven_what:1044367463976030288>')


async def nylo(ctx):
    await ctx.send('<:nylo:1044367439254798336>')


async def amogus(ctx):
    await ctx.send('ඞ')


async def amogus2(ctx):
    await ctx.send('𐐘')


async def amogus3(ctx):
    await ctx.send('𐑀')


async def bossy(ctx):
    await ctx.send(locale.get_string('bossyResponse'))


async def downloadupdate(ctx, bot):
    await ctx.send(locale.get_string('dlUpdate.start', prefix=config.PREFIX))

    yes_list = ['yes', 'ye', 'yeah', 'y']
    no_list = ['no', 'nah', 'nope', 'n']

    def check(m):
        return ((m.channel == ctx or m.channel == ctx.channel)
                and (m.content.lower() in yes_list or m.content.lower() in no_list))

    try:
        response = await bot.wait_for('message', timeout=60, check=check)

        if response.content in no_list:
            sleep(1)
            return await ctx.send(locale.get_string('dlUpdate.badResponse'))

        if response.content in yes_list:
            msg = await ctx.send(locale.get_string('dlUpdate.downloading0%'))
            sleep(1)
            await msg.edit(content=locale.get_string('dlUpdate.downloading20%'))
            sleep(2.5)
            await msg.edit(content=locale.get_string('dlUpdate.downloading42%'))
            sleep(2.5)
            await msg.edit(content=locale.get_string('dlUpdate.downloading69%'))
            sleep(2.5)
            await msg.edit(content=locale.get_string('dlUpdate.downloading91%'))
            sleep(3)
            await msg.edit(content=locale.get_string('dlUpdate.downloading96%'))
            sleep(4)
            await msg.edit(content=locale.get_string('dlUpdate.downloading99%1'))
            sleep(1.5)
            await msg.edit(content=locale.get_string('dlUpdate.downloading99%2'))
            sleep(1.5)
            await msg.edit(content=locale.get_string('dlUpdate.downloading99%3'))
            sleep(1.5)
            await msg.edit(content=locale.get_string('dlUpdate.downloading99%4'))
            sleep(3)
            if random() < .9:
                await msg.edit(content=locale.get_string('dlUpdate.downloadingError'))
                sleep(2)
                await ctx.send(locale.get_string('dlUpdate.dlExpletive'))
                sleep(2)
                await ctx.send(locale.get_string('dlUpdate.tryAgainLater'))
            else:
                await msg.edit(content=locale.get_string('dlUpdate.downloadingSuccess'))
                sleep(2)
                await ctx.send(locale.get_string('dlUpdate.shockAndAwe'))
                sleep(2)
                await ctx.send(locale.get_string('dlUpdate.actuallyWorkedDisbelief'))

    except asyncio.TimeoutError:
        await ctx.send(locale.get_string('dlUpdate.responseWaitedTooLong'))
