import discord
from random import choices

import config.config as config
from core.log import log


class Option():
    def __init__(self, func, weight, arg=None):
        self.func = func
        self.weight = weight
        self.arg = arg

    async def execute(self, ctx):
        await self.func(ctx, self.arg)


async def choose(ctx):
    options = [
        Option(send_image, 500, 'stop doing nomic.png'),
        Option(send_image, 10, 'absolute fools.png'),
        Option(send_image, 10, 'become unpoderable.png'),
        Option(send_image, 10, 'big brain granny.png'),
        Option(send_image, 10, 'birb vs ml.png'),
        Option(send_image, 10, 'mexican hankerchief.gif'),
        Option(send_image, 10, 'square stop doing nomic.png'),
        Option(send_image, 10, 'stop doing cfjs.png'),
        Option(send_image, 10, 'stop doing math.png'),
        Option(send_image, 10, 'stop doing medicine.jpg'),
        Option(send_image, 10, 'stop doing plantnomic.png'),
        Option(send_image, 10, 'stop doing.png'),
        Option(send_image, 10, 'trungified stop doing.png'),
        Option(send_image, 10, 'you could make a nomic.png'),
    ]

    option = choices(options, weights=[option.weight for option in options])[0]

    await option.execute(ctx)


####################
# Choice functions #
####################


async def send_image(ctx, filename):
    async with ctx.typing():
        with open(f'{config.SDN_DIR}/{filename}', 'rb') as file:
            f = discord.File(file, filename=filename)

        await ctx.send(file=f)
