import logging
import os
from PIL.Image import open as image_open, Image, new as new_image
import random
import pathlib

from discord import File, Embed
from discord.ext.bridge import BridgeExtContext

from .BladesCommandException import BladesCommandException

logger = logging.getLogger('bot')
asset_folder_rel_path = os.sep.join(["Assets", ""])

blades_dice_sprite_size = 64
sided_die_sprite_size = 64
nr_size = (17, 26)
nrs_index_within_spritesheet = 7  # where are the numbers in relation to the sprite columns


def get_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, asset_folder_rel_path)


async def blades_roll_command(ctx: BridgeExtContext, dice_amount: int):
    erg, rolled_array = get_blades_roll(dice_amount)
    spritesheet = image_open(get_blade_dice_spritesheet_filepath()).convert('RGBA')
    dice_sprite_size = get_blades_sprite_size()
    new_image = generate_end_image(dice_amount if dice_amount > 0 else 2, dice_sprite_size, 100, True)
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


async def all_size_roll(ctx: BridgeExtContext, dice_amount: int, dice_type: int):
    rolled_array = get_roll(dice_amount, dice_type)
    if dice_amount <= 10 and dice_type <= 100:
        # generate image
        max_columns = 5
        spritesheet = image_open(get_sized_dice_spritesheet_filepath()).convert('RGBA')
        base_sprite_indx = get_base_sprite_indx(dice_type)
        die_size = get_sided_die_sprite_size()
        base_image = get_sprite_from_uniform_spritesheet(spritesheet, die_size, base_sprite_indx)
        end_image = generate_end_image(dice_amount, die_size, max_columns, True)
        # Combine image with numbers and paste onto the result
        index = 0
        for nr_rolled, amount_rolled in enumerate(rolled_array):
            for _ in range(amount_rolled):
                logger.info(f"here8, {nr_rolled}")
                paste_nr_image(spritesheet, end_image, base_image, index, max_columns, nr_rolled)
                logger.info(f"here8, {nr_rolled}.2")
                index += 1
        merged_file_path = get_asset_folder_filepath() + "merged.png"
        end_image.save(merged_file_path, "PNG")
        await ctx.respond(file=File(merged_file_path))
        os.remove(merged_file_path)
    else:
        sum_val = 0
        nr_attachment = "Numbers rolled:\n"
        for indx, val in enumerate(rolled_array):
            if val > 0:
                nr_attachment += f"**{indx + 1}**: {val} times\n"
                sum_val += (indx + 1) * val
        await ctx.respond(embed=Embed(title=f"**{dice_amount}d{dice_type}= {sum_val}**", description=nr_attachment))


def paste_nr_image(spritesheet: Image, end_image: Image, base_image: Image, index: int, max_columns: int,
                   nr_rolled_index: int):
    nr_offset = (15, 19)
    nr_rolled = nr_rolled_index + 1
    die_sprite_size = base_image.size[0]
    sprite_table_paste_image(end_image, base_image, die_sprite_size, (0, 0), max_columns, index)
    if nr_rolled < 10:
        nr_image = get_die_nr_image(spritesheet, nr_rolled_index)
        nr_offset = (nr_offset[0] + int(nr_image.size[0]/2), nr_offset[1])
        sprite_table_paste_image(end_image, nr_image, die_sprite_size, nr_offset, max_columns, index)
    elif 10 <= nr_rolled < 100:
        first_nr_index = int(nr_rolled / 10) - 1
        second_nr_index = nr_rolled % 10 - 1
        second_nr_index = second_nr_index if second_nr_index >= 0 else 9
        nr_image = get_die_nr_image(spritesheet, first_nr_index)
        nr_image2 = get_die_nr_image(spritesheet, second_nr_index)
        sprite_table_paste_image(end_image, nr_image, die_sprite_size, nr_offset, max_columns, index, 0)
        sprite_table_paste_image(end_image, nr_image2, die_sprite_size, nr_offset, max_columns, index, 1)
    elif nr_rolled == 100:
        nr_image = get_die_nr_image(spritesheet, 0)
        nr_image2 = get_die_nr_image(spritesheet, 9)
        nr_offset = (nr_offset[0] - int(nr_image.size[0]/4), nr_offset[1])
        sprite_table_paste_image(end_image, nr_image, die_sprite_size, nr_offset, max_columns, index, 0, 1)
        sprite_table_paste_image(end_image, nr_image2, die_sprite_size, nr_offset, max_columns, index, 1, 1)
        sprite_table_paste_image(end_image, nr_image2, die_sprite_size, nr_offset, max_columns, index, 2, 1)


def get_blades_roll(dice_amount: int):
    rolled_max = 1
    if dice_amount > 10 or dice_amount < 0:
        raise BladesCommandException("please input a dice amount from 0 to 10")
    rolled_array = [0, 0, 0, 0, 0, 0]  # dice amounts are tracked in reverse. rolled_array[0] = amount of 6's rolled

    if dice_amount == 0:  # user rolls with disadvantage for this
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        rolled_array[6 - roll1] += 1
        rolled_array[6 - roll2] += 1
        rolled_max = min(roll1, roll2)
    else:
        for _ in range(dice_amount):
            roll = random.randint(1, 6)
            rolled_max = max(rolled_max, roll)
            rolled_array[6 - roll] += 1

    if rolled_array[0] > 1 and not dice_amount == 0:
        result = 2  # crit
    elif rolled_max <= 3:
        result = -1  # fail
    elif rolled_max <= 5:
        result = 0  # partial success
    else:
        result = 1  # success

    return result, rolled_array


def get_roll(amount: int, dice_size: int):
    if amount > 100 or amount < 1:
        raise BladesCommandException("cannot roll more than 100 dice or less than 1")
    if dice_size < 0:
        raise BladesCommandException("Please input a positive number for dice size")
    rolled_array = [0] * dice_size

    for _ in range(amount):
        rolled_array[random.randint(0, dice_size - 1)] += 1

    return rolled_array


def get_die_nr_image(spritesheet: Image, index: int):
    global nrs_index_within_spritesheet, nr_size
    if 0 > index or index > 10:
        logger.error(f"tried number that isn't valid {index}")
        raise BladesCommandException(
            "FATAL Error. Tried to get image for an invalid number. This should never happen. Contact the bot creator.")
    sheet_size = spritesheet.size
    dice_per_row = int(sheet_size[0] / get_sided_die_sprite_size())
    start_x = (nrs_index_within_spritesheet % dice_per_row) * get_sided_die_sprite_size()
    start_y = int(nrs_index_within_spritesheet / dice_per_row) * get_sided_die_sprite_size()
    cols = int((sheet_size[0] - start_x) / nr_size[0])

    # crop amounts
    left = start_x + (index % cols) * nr_size[0]
    right = left + nr_size[0]
    top = start_y + int(index / cols) * nr_size[1]
    bottom = top + nr_size[1]
    return spritesheet.crop((left, top, right, bottom))


def generate_end_image(sprite_amount, sprite_size, max_columns: int, transparent=False) -> Image:
    end_image_length = sprite_size * sprite_amount if sprite_amount < max_columns else sprite_size * max_columns
    end_image_height = sprite_size * (int(sprite_amount / max_columns) + (1 if sprite_amount % max_columns != 0 else 0))
    return new_image('RGBA',
                     (end_image_length, end_image_height),
                     (250, 250, 250, 0) if transparent else (250, 250, 250))


def sprite_table_paste_image(parent_image: Image,
                             paste_image: Image,
                             die_sprite_size: int,
                             offset: tuple[int, int],
                             max_columns: int, index: int,
                             subnumber_index: int = 0,
                             side_crop: int = 0
                             ):
    row = int(index / max_columns)
    col = index % max_columns
    temp_image = paste_image.crop((side_crop, 0, paste_image.size[0] - side_crop, paste_image.size[1]))
    parent_image.paste(
        temp_image,
        (
            offset[0] + (temp_image.size[0] - side_crop * 2) * subnumber_index + die_sprite_size * col,
            offset[1] + die_sprite_size * row
        ),
        temp_image)


def get_die_base_image_filepath(nr: int):
    return get_asset_folder_filepath() + os.sep.join(["dice", f"dice_base-{nr}.png"])


def get_blade_dice_spritesheet_filepath():
    return get_asset_folder_filepath() + os.sep.join(["dice", "Blades_dice_spritesheet.png"])


def get_sized_dice_spritesheet_filepath():
    return get_asset_folder_filepath() + os.sep.join(["dice", "sized_dice_spritesheet.png"])


def get_tag_spritesheet_filepath():
    return get_asset_folder_filepath() + os.sep.join(["dice", "blades_success_tags.png"])


def get_success_tag_sprite(success: int):
    if 2 < success or success < -1:
        raise BladesCommandException("Blades/get_success_tag: Tried to get success tag outside of range")

    spritesheet = image_open(get_tag_spritesheet_filepath()).convert('RGBA')
    success_tag = None
    width, height = spritesheet.size

    if success == 0:
        return spritesheet.crop((0, 0, int(width / 3), 32))
    if success == -1:
        success_tag = spritesheet.crop((0, 32, int(width / 3), height))
    elif success == 1:
        success_tag = spritesheet.crop((int(width / 3), 32, int(width / 3) * 2, height))
    elif success == 2:
        success_tag = spritesheet.crop((int(width / 3) * 2, 32, width, height))

    return success_tag


def get_blades_sprite_size():
    global blades_dice_sprite_size
    return blades_dice_sprite_size


def get_sided_die_sprite_size():
    global sided_die_sprite_size
    return sided_die_sprite_size


def get_sprite_from_uniform_spritesheet(spritesheet: Image, sprite_size: int, index: int):
    sheet_size = spritesheet.size
    columns = int(sheet_size[0] / sprite_size)
    # crop amounts
    left = (index % columns) * sprite_size
    right = left + sprite_size
    top = int(index / columns) * sprite_size
    bottom = top + sprite_size
    return spritesheet.crop((left, top, right, bottom))


def get_base_sprite_indx(dice_size):
    if dice_size == 20:
        return 0
    if dice_size == 4:
        return 1
    if dice_size == 6:
        return 2
    if dice_size == 8:
        return 3
    if dice_size == 10:
        return 4
    if dice_size == 12:
        return 5
    return 6
