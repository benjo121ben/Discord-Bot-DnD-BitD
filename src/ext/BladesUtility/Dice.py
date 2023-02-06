import logging
import os
from PIL import Image
import random
import pathlib

from discord import File, Embed

from .BladesCommandException import BladesCommandException

logger = logging.getLogger('bot')
asset_folder_rel_path = os.sep.join(["Assets", ""])

blades_dice_sprite_size = 64


def get_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, asset_folder_rel_path)


async def blades_roll_command(ctx, dice_amount: int):
    erg, rolled_array = get_blades_roll(dice_amount)
    spritesheet = Image.open(get_spritesheet_filepath()).convert('RGBA')
    dice_sprite_size = get_sprite_size()
    end_image_length = dice_sprite_size * dice_amount if dice_amount > 0 else 2 * dice_sprite_size
    end_image_height = dice_sprite_size
    new_image = Image.new('RGBA', (end_image_length, end_image_height), (250, 250, 250))
    # Read the two images
    all_rolls_index = 0
    for array_index, amount_rolled in enumerate(rolled_array):
        nr_rolled = 6 - array_index
        if nr_rolled == 6 and erg == 2:
            nr_rolled = 7
        nr_image = get_sprite_from_uniform_spritesheet(spritesheet, dice_sprite_size, nr_rolled - 1)
        for _ in range(amount_rolled):
            new_image.paste(nr_image, (dice_sprite_size * all_rolls_index, 0), nr_image)
            all_rolls_index += 1
    success_file_path = get_asset_folder_filepath() + "success.png"
    merged_file_path = get_asset_folder_filepath() + "merged.png"

    get_success_tag_sprite(erg).save(success_file_path, "PNG")
    new_image.save(merged_file_path, "PNG")

    embed = Embed(title=f'Rolled {dice_amount} dice')
    embed.set_image(url='attachment://merged.png')
    embed.set_thumbnail(url='attachment://success.png')
    await ctx.respond(embed=embed, files=[File(success_file_path), File(merged_file_path)])
    os.remove(success_file_path)
    os.remove(merged_file_path)


async def all_size_roll(ctx, dice_amount, dice_type):
    rolled_array = get_roll(dice_amount, dice_type)
    base_image = Image.open(get_die_base_image_filepath(dice_type)).convert('RGBA')
    new_dice_size = base_image.size
    new_image = Image.new('RGBA', (new_dice_size[0] * dice_amount, new_dice_size[1]), (250, 250, 250))
    # Read the two images
    index = 0
    for nr_rolled, amount_rolled in enumerate(rolled_array):
        for _ in range(amount_rolled):
            nr_image = Image.open(get_die_nr_image_filepath(nr_rolled + 1)).convert('RGBA')
            new_image.paste(base_image, (0 + 150 * index, 0))
            new_image.paste(nr_image, (50 + 150 * index, 50), nr_image)
            index += 1
    merged_file_path = get_asset_folder_filepath() + "merged.png"
    new_image.save(merged_file_path, "PNG")
    await ctx.respond(file=File(merged_file_path))
    os.remove(merged_file_path)


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
        return spritesheet.crop((0, 0, int(width/3), 32))
    if success == -1:
        success_tag = spritesheet.crop((0, 32, int(width/3), height))
    elif success == 1:
        success_tag = spritesheet.crop((int(width/3), 32, int(width/3)*2, height))
    elif success == 2:
        success_tag = spritesheet.crop((int(width/3)*2, 32, width, height))

    return success_tag


def get_sprite_size():
    return blades_dice_sprite_size


def get_sprite_from_uniform_spritesheet(spritesheet: Image, sprite_size: int, index: int):
    sheet_size = spritesheet.size
    columns = int(sheet_size[0] / sprite_size)
    # crop amounts
    left = (index % columns) * sprite_size
    right = left + sprite_size
    top = int(index / columns) * sprite_size
    bottom = top + sprite_size
    return spritesheet.crop((left, top, right, bottom))


