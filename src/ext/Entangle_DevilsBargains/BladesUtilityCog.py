from discord import slash_command
from discord.ext import commands
from discord.ext import bridge
from .functions import db_functionality, db_single_functionality, check_devils_bargain, \
    entanglement_functionality, check_entanglements


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


def setup(bot: bridge.Bot):
    # Every extension should have this function
    check_entanglements()
    check_devils_bargain()
    bot.add_cog(BladesUtilityCog())


