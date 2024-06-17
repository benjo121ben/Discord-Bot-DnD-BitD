import logging
import os
import pathlib

from PIL.Image import open as image_open, Image, new as create_new_image, Resampling
from discord import File

from .ResourceTracker import ResourceTracker

logger = logging.getLogger('bot')

in_between_sprite_size = [5, 16]
stress_bar_sprite_size = [16, 32]


def fill_end_image(spritesheet: Image, end_image: Image, stress_tracker: ResourceTracker):
    global in_between_sprite_size, stress_bar_sprite_size
    bar_sprite, filled_sprite, in_between_sprite = get_sprites_from_spritesheet(spritesheet)

    def calc_start(index: int):
        return 2 + stress_bar_sprite_size[0] * index + index * 3

    for index in range(stress_tracker.max_resource):
        end_image.paste(bar_sprite, (calc_start(index), 0), bar_sprite)
    for index in range(stress_tracker.value):
        end_image.paste(filled_sprite, (calc_start(index), 0), filled_sprite)
    for index in range(stress_tracker.max_resource - 1):
        end_image.paste(in_between_sprite, (calc_start(index + 1) - in_between_sprite_size[0] + 1, 0), in_between_sprite)


def get_sprites_from_spritesheet(spritesheet: Image) -> (Image, Image, Image):
    global in_between_sprite_size, stress_bar_sprite_size
    bar_sprite = spritesheet.crop((0, 0, stress_bar_sprite_size[0], stress_bar_sprite_size[1]))
    filled_sprite = spritesheet.crop((stress_bar_sprite_size[0], 0, stress_bar_sprite_size[0]*2, stress_bar_sprite_size[1]))
    in_between_sprite = spritesheet.crop((0, stress_bar_sprite_size[1], in_between_sprite_size[0], stress_bar_sprite_size[1] + in_between_sprite_size[1]))
    return bar_sprite, filled_sprite, in_between_sprite


def generate_end_image(width_count: int) -> Image:
    global in_between_sprite_size, stress_bar_sprite_size
    end_image_length = width_count * stress_bar_sprite_size[0] + (width_count - 1) * (in_between_sprite_size[0] - 2) + 4 # +4 is back and front margin
    end_image_height = stress_bar_sprite_size[1]
    return create_new_image('RGBA',
                            (end_image_length, end_image_height),
                            (79, 79, 79, 250))


def get_blade_dice_spritesheet_filepath() -> str:
    return get_asset_folder_filepath() + os.sep.join(["blades_stress_bar.png"])


def get_asset_folder_filepath() -> str:
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, os.sep.join(["Assets", ""]))


def build_stress_track_image(stress_tracker: ResourceTracker) -> str:
    spritesheet = image_open(get_blade_dice_spritesheet_filepath()).convert('RGBA')
    new_image = generate_end_image(stress_tracker.max_resource)
    fill_end_image(spritesheet, new_image, stress_tracker)
    merged_file_path = get_asset_folder_filepath() + "merged.png"

    new_image.resize((new_image.size[0] * 2, new_image.size[1] * 2), resample=Resampling.NEAREST).save(
        merged_file_path, "PNG")
    return merged_file_path
