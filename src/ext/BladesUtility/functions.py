import os
from os.path import exists
import json
import pathlib
import random
from random import uniform, seed
from datetime import datetime

from discord import File, Embed

from .Entanglement_table import Entanglement_sorting_table

seed(datetime.now().timestamp())

imported_expanded_entanglements = {}
db_asset_folder_rel_path = "..\\..\\..\\Assets\\DB\\"
entangle_asset_folder_rel_path = "..\\..\\..\\Assets\\"

entanglements_enabled = False
devils_bargains_enabled = False


class BladesCommandException(Exception):
    pass


def get_db_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, db_asset_folder_rel_path)


def get_entanglement_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, entangle_asset_folder_rel_path)


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

    if not 0 < nr < 51:
        ctx.respond("A card with this number does not exist.")
        return

    if nr < 10:
        nr = "0" + str(nr)
    await ctx.respond(file=File(get_db_asset_folder_filepath() + "DevilsBargain-" + str(nr) + ".png"))


async def entanglement_functionality(ctx, rolled: int, heat: int):
    if not entanglements_enabled:
        await ctx.respond("Entanglements are missing, therefore this command was automatically deactivated.")
        return

    column = -1
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


def get_devils_bargain():
    rand = int(uniform(1, 50))
    if rand < 10:
        rand = "0" + str(rand)
    return File(f"{get_db_asset_folder_filepath()}DevilsBargain-{rand}.png")


def get_blades_roll(amount: int):
    erg = 1
    if amount > 10 or amount < 0:
        raise BladesCommandException("cannot roll more than 10 dice")
    rolled_array = [0, 0, 0, 0, 0, 0]

    if amount == 0:  # user rolls with disadvantage for this
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        rolled_array[roll1-1] += 1
        rolled_array[roll2-1] += 1
        erg = min(roll1, roll2)
    else:
        for _ in range(amount):
            roll = random.randint(1, 6)
            erg = max(erg, roll)
            rolled_array[roll-1] += 1
    if erg <= 3:
        erg = -1
    elif erg <= 5:
        erg = 0
    else:
        erg = 1
        if rolled_array[5] > 1:
            erg = 2

    return erg, rolled_array


def get_die_nr_image_filepath(nr: int):
    return get_entanglement_asset_folder_filepath() + f"dice\\{nr}.png"


def get_die_base_image_filepath(nr: int):
    return get_entanglement_asset_folder_filepath() + f"dice\\dice_base-{nr}.png"


def check_devils_bargain():
    global devils_bargains_enabled
    if not exists(get_db_asset_folder_filepath()):
        print(f"Cannot find devils bargain asset folder:\n"
              f"{get_db_asset_folder_filepath()}"
              f"Devils Bargain Feature disabled")
        return
    devils_bargains_enabled = True
    for i in range(1, 50):
        nr = str(i)
        if i < 10:
            nr = "0" + str(i)
        if not os.path.exists(get_db_asset_folder_filepath() + "DevilsBargain-" + nr + ".png"):
            devils_bargains_enabled = False
            print("DevilsBargain-" + nr + ".png", "missing")
    if not devils_bargains_enabled:
        print("Devils Bargains disabled, due to missing Files\n")
    else:
        print("Devils Bargains present, feature enabled\n")


def check_entanglements():
    global imported_expanded_entanglements, entanglements_enabled
    if not exists(f'{get_entanglement_asset_folder_filepath()}\\Expanded_Entanglements.json'):
        print(f"Expanded_Entanglements.json cannot be found at location:\n"
              f"{get_entanglement_asset_folder_filepath()}\n"
              f"entanglements disabled")
        return
    entanglements_enabled = True
    imported_expanded_entanglements = json.load(open(f'{get_entanglement_asset_folder_filepath()}\\Expanded_Entanglements.json'))
    print("looking for entanglements")
    for column in Entanglement_sorting_table:
        for roll in column:
            for entanglement in roll:
                if entanglement not in imported_expanded_entanglements:
                    entanglements_enabled = False
                    print("missing", entanglement)
    if not entanglements_enabled:
        print("Entanglements disabled, due to missing entanglements\n")
    else:
        print("Entanglements present, feature enabled\n")
