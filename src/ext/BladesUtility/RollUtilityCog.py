import logging
from discord import slash_command
from discord.ext import commands
from discord.ext import bridge

from .BladesCommandException import BladesCommandException
from .Dice import all_size_roll

logger = logging.getLogger('bot')


class RollUtilityCog(commands.Cog):

    @slash_command(name="roll", description="tests the all roll")
    async def types_roll(self, ctx, dice_amount: int, dice_size: int):
        try:
            await all_size_roll(ctx, dice_amount, dice_size)
        except BladesCommandException as e:
            await ctx.respond(str(e))


def setup(bot: bridge.Bot):
    # Every extension should have this function
    logger.debug("setting up Blades Cog")
    bot.add_cog(RollUtilityCog())


