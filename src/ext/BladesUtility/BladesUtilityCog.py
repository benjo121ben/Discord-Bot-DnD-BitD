import logging
from discord import slash_command
from discord.ext import commands
from discord.ext import bridge

from .BladesCommandException import BladesCommandException
from .DevilsBargainDeck import db_functionality, db_single_functionality, check_devils_bargain_assets
from .EntanglementFunctions import entanglement_functionality, check_entanglement_assets
from .Dice import blades_roll_command, all_size_roll
from .ItemWiki import setup_wiki, wiki_search

logger = logging.getLogger('bot')


class BladesUtilityCog(commands.Cog):

    @slash_command(name="devils_bargain", description="Returns one or more random devils bargain cards. Default: 1 card")
    async def devils_bargain(self, ctx, nr: int = 1):
        await db_functionality(ctx, nr)

    @slash_command(name="db_by_nr", description="Returns the Devils Bargain Card with with this number")
    async def devils_bargain_by_nr(self, ctx, nr: int):
        await db_single_functionality(ctx, nr)

    @slash_command(name="entanglement", description="Prints out the entanglement choices for the given rolled value and heat")
    async def entanglements(self, ctx, rolled: int, heat: int):
        await entanglement_functionality(ctx, rolled, heat)

    @slash_command(name="b_roll", description="tests the blades roll")
    async def blades_roll(self, ctx, dice_amount: int):
        try:
            await blades_roll_command(ctx, dice_amount)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="roll", description="tests the all roll")
    async def types_roll(self, ctx, dice_amount: int, dice_type: int):
        await all_size_roll(ctx, dice_amount, dice_type)

    @slash_command(name="wiki",
                   description="Prints out the item description for the selected item")
    async def wiki(self, ctx, item_name: str):
        await wiki_search(ctx, item_name)


def setup(bot: bridge.Bot):
    # Every extension should have this function
    logger.debug("setting up Blades Cog")
    check_entanglement_assets()
    check_devils_bargain_assets()
    setup_wiki()
    bot.add_cog(BladesUtilityCog())


