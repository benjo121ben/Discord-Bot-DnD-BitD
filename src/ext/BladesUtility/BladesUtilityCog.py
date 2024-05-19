import logging
from discord import slash_command, ApplicationContext
from discord.commands import option
from discord.ext import commands

from .BladesCommandException import BladesCommandException
from .DevilsAndEntanglements.DevilsBargainDeck import db_functionality, check_devils_bargain_assets
from .DevilsAndEntanglements.EntanglementFunctions import entanglement_functionality, check_entanglement_assets, \
    entanglement_wanted_functionality
from .Dice import blades_roll_command
from .Wiki.ItemWiki import setup_wiki, wiki_search
from ...ContextInfo import init_context

logger = logging.getLogger('bot')


class BladesUtilityCog(commands.Cog):

    @slash_command(name="devils_bargain", description="Returns one or more random devils bargain cards. Default: 1 card")
    async def devils_bargain(self, ctx: ApplicationContext, nr: int = 1):
        try:
            await db_functionality(ctx, nr)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="entanglement", description="Returns appropriate entanglement choices. Takes the value rolled in the wanted roll and crew heat")
    async def entanglements(self, ctx: ApplicationContext, rolled: int, heat: int):
        try:
            await entanglement_functionality(ctx, rolled, heat)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="entanglement_wanted",
                   description="Rolls for entanglement. Takes in the wanted level and crew heat.")
    async def entanglements_wanted(self, ctx: ApplicationContext, wanted: int, heat: int):
        try:
            await entanglement_wanted_functionality(ctx, wanted, heat)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="bladeroll", description="Make a d6 roll using the Blades in the Dark rules")
    @option(name="dice_amount", description="the amount of dice you want to roll")
    @option(name="sorted_dice", description="do you wish to sort your dice?")
    async def blades_roll(self, ctx: ApplicationContext, dice_amount: int, sorted_dice: bool = False):
        try:
            await blades_roll_command(ctx, dice_amount, sorted_dice=sorted_dice)
        except BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="wiki",
                   description="Prints out the item description for the selected item")
    async def wiki(self, ctx: ApplicationContext, entry_name: str):
        try:
            await wiki_search(await init_context(ctx=ctx), entry_name)
        except BladesCommandException as e:
            await ctx.respond(str(e))


def setup(bot: commands.Bot):
    # Every extension should have this function
    logger.debug("setting up Blades Cog")
    check_entanglement_assets()
    check_devils_bargain_assets()
    setup_wiki()
    bot.add_cog(BladesUtilityCog())


