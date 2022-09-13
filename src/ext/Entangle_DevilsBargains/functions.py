import os
from os.path import exists
import json
from random import uniform, seed
from datetime import datetime

from discord import File, Embed

from .Entanglement_table import Entanglement_sorting_table

seed(datetime.now().timestamp())

imported_expanded_entanglements = {}
devils_bargain_images_path = "Assets/DB/"

entanglements_enabled = False
devils_bargains_enabled = False


async def db_functionality(ctx, amount: int = 1):
    if not devils_bargains_enabled:
        await ctx.respond("Devils Bargains are missing, therefore this command was automatically deactivated.")
        return

    if amount > 1:
        amount = min(10, amount)
        file_list: list[File] = []
        for i in range(0, amount):
            file_list.append(get_devils_bargain())
        await ctx.respond(files=file_list)
    else:
        await ctx.respond(file=get_devils_bargain())


async def db_single_functionality(ctx, nr: int):
    if not devils_bargains_enabled:
        await ctx.respond("Devils Bargains are missing, therefore this command was automatically deactivated.")
        return

    if 0 < nr < 51:
        await ctx.respond(file=File(devils_bargain_images_path + "DevilsBargain-" + str(nr) + ".png"))
    else:
        ctx.respond("A card with this number does not exist.")


async def entanglement_functionality(ctx, rolled: int, heat: int):
    if not entanglements_enabled:
        await ctx.respond("Entanglements are missing, therefore this command was automatically deactivated.")
        return

    column = None
    if heat <= 3:
        column = 0
    elif heat <= 5:
        column = 1
    else:
        column = 2

    if rolled < 1 or rolled > 6:
        await ctx.respond("The number rolled has to be between 1 and 6")
        return
    rolled -= 1
    ent_list = Entanglement_sorting_table[column][rolled]
    embed = Embed(title="Entanglements", description="choose one!")
    for entanglement in ent_list:
        embed.add_field(name=entanglement, value=imported_expanded_entanglements[entanglement], inline=True)
    await ctx.respond(embed=embed)


def get_devils_bargain(nr: int = -1):
    rand = int(uniform(1, 50))
    if rand < 10:
        rand = "0" + str(rand)
    return File(devils_bargain_images_path + "DevilsBargain-" + str(rand) + ".png")


def check_devils_bargain():
    global devils_bargains_enabled
    if not exists(devils_bargain_images_path):
        return
    devils_bargains_enabled = True
    for i in range(1,50):
        nr = str(i)
        if i < 10:
            nr = "0" + str(i)
        if not os.path.exists(devils_bargain_images_path + "DevilsBargain-" + nr + ".png"):
            devils_bargains_enabled = False
            print("DevilsBargain-" + nr + ".png", "missing")
    if not devils_bargains_enabled:
        print("Devils Bargains disabled, due to missing Files\n")
    else:
        print("Devils Bargains present, feature enabled\n")


def check_entanglements():
    global imported_expanded_entanglements, entanglements_enabled
    if not exists('Assets/Expanded_Entanglements.json'):
        return
    entanglements_enabled = True
    imported_expanded_entanglements = json.load(open('Assets/Expanded_Entanglements.json'))
    print("looking for entanglements")
    for column in Entanglement_sorting_table:
        for roll in column:
            for entanglement in roll:
                if not imported_expanded_entanglements.__contains__(entanglement):
                    entanglements_enabled = False
                    print("missing", entanglement)
    if not entanglements_enabled:
        print("Entanglements disabled, due to missing entanglements\n")
    else:
        print("Entanglements present, feature enabled\n")
