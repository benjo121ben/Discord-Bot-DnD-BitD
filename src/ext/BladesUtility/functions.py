import os
from PIL import Image
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
db_asset_folder_rel_path = os.sep.join(["..","..", "..", "Assets", "DB", ""])
asset_folder_rel_path = os.sep.join(["..", "..", "..", "Assets", ""])


entanglements_enabled = False
devils_bargains_enabled = False
blades_dice_sprite_size = 64


class BladesCommandException(Exception):
    pass


def get_db_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, db_asset_folder_rel_path)


def get_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, asset_folder_rel_path)


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


def get_blades_roll(dice_amount: int):
    rolled_max = 1
    if dice_amount > 10 or dice_amount < 0:
        raise BladesCommandException("cannot roll more than 10 dice")
    rolled_array = [0, 0, 0, 0, 0, 0]  # dice amounts are tracked in reverse. rolled_array[0] = amount of 6's rolled

    if dice_amount == 0:  # user rolls with disadvantage for this
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        rolled_array[6-roll1] += 1
        rolled_array[6-roll2] += 1
        rolled_max = min(roll1, roll2)
    else:
        for _ in range(dice_amount):
            roll = random.randint(1, 6)
            rolled_max = max(rolled_max, roll)
            rolled_array[6-roll] += 1

    if rolled_array[0] > 1 and not dice_amount == 0:
        result = 2   # crit
    elif rolled_max <= 3:
        result = -1  # fail
    elif rolled_max <= 5:
        result = 0  # partial success
    else:
        result = 1  # success

    return result, rolled_array


def get_roll(amount: int, type: int):
    if amount > 30 or amount < 1:
        raise BladesCommandException("cannot roll more than 30 dice or less than 1")
    rolled_array = [0] * type

    for _ in range(amount):
        roll = random.randint(1, type)
        rolled_array[roll-1] += 1

    return rolled_array


def get_die_nr_image_filepath(nr: int):
    return get_asset_folder_filepath() + os.sep.join(["dice", f"{nr}.png"])


def get_die_base_image_filepath(nr: int):
    return get_asset_folder_filepath() + os.sep.join(["dice", f"dice_base-{nr}.png"])


def get_spritesheet_filepath():
    return get_asset_folder_filepath() + os.sep.join(["dice", "Blades_dice_spritesheet.png"])


def get_tag_spritesheet_filepath():
    return get_asset_folder_filepath() + os.sep.join(["dice", "blades_success_tags.png"])


def get_success_tag_sprite(success: int):
    if 2 < success or success < -1:
        raise BladesCommandException("Blades/get_success_tag: Tried to get success tag outside of range")

    spritesheet = Image.open(get_tag_spritesheet_filepath()).convert('RGBA')
    success_tag = None
    width, height = spritesheet.size

    if success == 0:
        return spritesheet.crop((0, 0, 144, 32))
    if success == -1:
        success_tag = spritesheet.crop((0, 32, int(width/3), height))
    elif success == 1:
        success_tag = spritesheet.crop((int(width/3), 32, int(width/3)*2, height))
    elif success == 2:
        success_tag = spritesheet.crop((int(width/3)*2, 32, width, height))

    return success_tag


def get_sprite_size():
    return blades_dice_sprite_size


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


def get_sprite_from_uniform_spritesheet(spritesheet: Image, sprite_size: int, index: int):
    sheet_size = spritesheet.size
    columns = int(sheet_size[0] / sprite_size)
    # crop amounts
    left = (index % columns) * sprite_size
    right = left + sprite_size
    top = int(index / columns) * sprite_size
    bottom = top + sprite_size
    return spritesheet.crop((left, top, right, bottom))


def check_entanglements():
    global imported_expanded_entanglements, entanglements_enabled
    expanded_entanglement_path = os.sep.join([f'{get_asset_folder_filepath()}', 'Expanded_Entanglements.json'])
    if not exists(expanded_entanglement_path):
        print(f"Expanded_Entanglements.json cannot be found at location:\n"
              f"{get_asset_folder_filepath()}\n"
              f"entanglements disabled")
        return
    entanglements_enabled = True
    imported_expanded_entanglements = json.load(open(expanded_entanglement_path))

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
