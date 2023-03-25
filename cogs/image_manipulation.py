import discord
from discord.ext import commands

from core.log import log
import config.config as config
import core.utils as utils
import core.image as image

import core.language as language

locale = language.Locale('cogs.image_manipulation')


class Image_Manipulation(commands.Cog, name='Image Manipulation'):
    '''
    A collection of commands related to image manipulation.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Trungifies an image',
        help=('Attach or link to an image to trungify it.\n'
              'You can also reply another message that has an image with this '
              'command to trungify that image instead.'),
        aliases=['trung', 'tr', 'triangle', 'trungle', 'trunglo']
    )
    async def trungify(self, ctx):
        await _trung_handler(ctx, False, False)

    @commands.command(
        brief='Trungifies an image from the bottom',
        help=('Attach or link to an image to bottom trungify it.\n'
              'You can also reply another message that has an image with this '
              'command to bottom trungify that image instead.'),
        aliases=['bottrung', 'btr', 'updowntrung', 'updown', 'smallbrain']
    )
    async def bottomtrung(self, ctx):
        await _trung_handler(ctx, False, True)

    @commands.command(
        brief='Detrungifies an image',
        help=('Attach or link to an image to detrungify it.\n'
              'You can also reply another message that has an image with this '
              'command to detrungify that image instead.'),
        aliases=['detrungify', 'detrung', 'dtr', 'dt', 'antitrung']
    )
    async def bigbrain(self, ctx):
        await _trung_handler(ctx, True, False)

    @commands.command(
        brief='Detrungifies an image from the bottom',
        help=('Attach or link to an image to bottom detrungify it.\n'
              'You can also reply another message that has an image with this '
              'command to bottom detrungify that image instead.'),
        aliases=['bottomdetrungify', 'bottomdetrung', 'botdetrung', 'bdtr', 'bdt', 'updowndetrung']
    )
    async def thicc(self, ctx):
        await _trung_handler(ctx, True, True)


async def _trung_handler(ctx, detrung: bool, updown: bool):
    commandName = f'{config.PREFIX}{"detrungify" if detrung else "trungify"}'

    async def get_image_source():
        # Check if the message contains an image
        message = ctx.message
        if (
            len(message.attachments) > 0 and
            any(message.attachments[0].filename.endswith(e) for e in config.IMAGE_EXTENSIONS)
        ):
            return message.attachments[0].url

        if any(message.content.endswith(e) for e in config.IMAGE_EXTENSIONS):
            return utils.strip_command(message.content, commandName)

        # Check if a replied to message contains an image
        if message.reference:
            reply = await ctx.channel.fetch_message(ctx.message.reference.message_id)

            if (
                len(reply.attachments) > 0 and
                any(reply.attachments[0].filename.endswith(e) for e in config.IMAGE_EXTENSIONS)
            ):
                return reply.attachments[0].url

            if any(reply.content.endswith(e) for e in config.IMAGE_EXTENSIONS):
                return utils.strip_command(reply.content, commandName)

        # No valid image found
        return None

    source = await get_image_source()
    if source is None:
        await ctx.send(locale.get_string('imageNotSupported'))
        return

    try:
        async with ctx.typing():
            image.trungify_and_save(source, config.TRUNGIFY_CACHE, detrung, updown)

            with open(config.TRUNGIFY_CACHE, 'rb') as file:
                f = discord.File(file, filename=config.TRUNGIFY_CACHE)

            await ctx.send(file=f)
    except Exception as e:
        log.exception(e)
        await ctx.send(config.GENERIC_ERROR)


async def setup(bot):
    await bot.add_cog(Image_Manipulation(bot))
