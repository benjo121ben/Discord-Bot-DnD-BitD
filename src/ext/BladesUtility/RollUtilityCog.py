import logging
from discord import slash_command
from discord.commands import option
from discord.ext import commands
from discord.ext import bridge

from .BladesCommandException import BladesCommandException
from .Dice import all_size_roll_sorted, all_size_roll

logger = logging.getLogger('bot')


class RollUtilityCog(commands.Cog):

    @slash_command(name="roll", description="rolls dice of any size")
    @option(name="dice_amount", description="the amount of dice you want to roll")
    @option(name="dice_size", description="the size of your dice")
    @option(name="sorted_dice", description="do you wish to sort your dice?")
    async def types_roll(self, ctx, dice_amount: int, dice_size: int, sorted_dice: bool = False):
        try:
            if sorted_dice:
                await all_size_roll_sorted(ctx, dice_amount, dice_size)
            else:
                await all_size_roll(ctx, dice_amount, dice_size)
        except BladesCommandException as e:
            await ctx.respond(str(e))


def setup(bot: bridge.Bot):
    # Every extension should have this function
    logger.debug("setting up Blades Cog")
    bot.add_cog(RollUtilityCog())


