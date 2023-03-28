import logging
from discord import slash_command
from discord.ext import commands
from discord.ext import bridge

from .BladesCommandException import BladesCommandException
from .DevilsBargainDeck import db_functionality, check_devils_bargain_assets
from .EntanglementFunctions import entanglement_functionality, check_entanglement_assets
from .Dice import blades_roll_command
from .ItemWiki import setup_wiki, wiki_search

logger = logging.getLogger('bot')


class BladesUtilityCog(commands.Cog):

    @slash_command(name="devils_bargain", description="Returns one or more random devils bargain cards. Default: 1 card")
    async def devils_bargain(self, ctx, nr: int = 1):
        try:
            await db_functionality(ctx, nr)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    # @slash_command(name="db_by_nr", description="Returns the Devils Bargain Card with with this number")
    # async def devils_bargain_by_nr(self, ctx, nr: int):
    #     await db_single_functionality(ctx, nr)

    @slash_command(name="entanglement", description="Prints out the entanglement choices for the given rolled value and heat")
    async def entanglements(self, ctx, rolled: int, heat: int):
        try:
            await entanglement_functionality(ctx, rolled, heat)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="bladeroll", description="Make a d6 roll using the Blades in the Dark rules")
    async def blades_roll(self, ctx, dice_amount: int):
        try:
            await blades_roll_command(ctx, dice_amount)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="wiki",
                   description="Prints out the item description for the selected item")
    async def wiki(self, ctx, entry_name: str):
        try:
            await wiki_search(ctx, entry_name)
        except BladesCommandException as e:
            await ctx.respond(str(e))


def setup(bot: bridge.Bot):
    # Every extension should have this function
    logger.debug("setting up Blades Cog")
    check_entanglement_assets()
    check_devils_bargain_assets()
    setup_wiki()
    bot.add_cog(BladesUtilityCog())


