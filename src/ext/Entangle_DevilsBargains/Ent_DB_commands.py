from discord import slash_command
from discord.ext import commands
from discord.ext import bridge
from discord import Embed, File
from .functions import db_functionality, db_single_functionality, check_devils_bargain, \
    entanglement_functionality, check_entanglements


@slash_command(name="db")
async def devils_bargain(ctx, nr: int = 1):
    await db_functionality(ctx, nr)


@slash_command(name="db_nr")
async def devils_bargain_by_nr(ctx, nr: int):
    await db_single_functionality(ctx, nr)


@slash_command(name="ent")
async def entanglements(ctx, rolled: int, heat: int):
    await entanglement_functionality(ctx, rolled, heat)


def setup(bot: bridge.Bot):
    # Every extension should have this function
    check_entanglements()
    check_devils_bargain()
    bot.add_application_command(devils_bargain)
    bot.add_application_command(devils_bargain_by_nr)
    bot.add_application_command(entanglements)


