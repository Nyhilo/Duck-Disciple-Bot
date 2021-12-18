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
        if self.arg:
            return await self.func(ctx, self.arg)

        return await self.func(ctx)


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
        Option(hi, 5),
        Option(thistbh, 10),
        Option(amogus, 10),
        Option(bossy, 1),
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


async def hi(ctx):
    await ctx.send('hi```\n```')


async def thistbh(ctx):
    await ctx.send('<:this:730549270532325456>')


async def amogus(ctx):
    await ctx.send('ඞ')


async def bossy(ctx):
    await ctx.send('*"Stop doing nomic", "what time is it?", "trungify this meme", "pool roll some bullshit".*\n\n'
                   "Don't you all have anything better to do?")
