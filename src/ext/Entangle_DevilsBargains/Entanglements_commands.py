import os
from discord.ext import commands
from discord import Embed
import src.GlobalVariables as globalVars
from .Entanglement_table import *


@commands.command(name="ent")
async def entanglements(ctx, rolled: int, heat: int):
    if not globalVars.entanglements_exist:
        await ctx.send("Entanglements are missing, therefore this command was automatically deactivated.")
        return

    column = None
    if heat <= 3:
        column = 0
    elif heat <= 5:
        column = 1
    else:
        column = 2

    if rolled < 1 or rolled > 6:
        await ctx.send("The number rolled has to be between 1 and 6")
        return
    rolled -= 1
    ent_list = Entanglement_sorting_table[column][rolled]
    embed = Embed(title="Entanglements", description="choose one!")
    for entanglement in ent_list:
        embed.add_field(name=entanglement, value=globalVars.imported_expanded_entanglements[entanglement], inline=True)
    await ctx.send(embed=embed)


def check_entanglements():
    print("looking for entanglements")
    globalVars.entanglements_exist = True
    for column in Entanglement_sorting_table:
        for roll in column:
            for entanglement in roll:
                if not globalVars.imported_expanded_entanglements.__contains__(entanglement):
                    globalVars.entanglements_exist = False
                    print("missing", entanglement)
    if not globalVars.entanglements_exist:
        print("Entanglements disabled, due to missing entanglements")
    else:
        print("Entanglements present, feature enabled")
    print()


def setup(bot: commands.bot.Bot):
    # Every extension should have this function
    check_entanglements()
    bot.add_command(entanglements)
