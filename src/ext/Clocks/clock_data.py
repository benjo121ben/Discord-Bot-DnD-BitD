import logging
from os.path import exists
from discord import File
import os

import pathlib


clock_files_dic = {}
clocks_rel_asset_folder_path = os.sep.join(['Assets', ''])

logger = logging.getLogger('bot')


class NoClockImageException(Exception):
    pass


class Clock:
    def __init__(self, _name: str, _size: int, _ticks: int = 0):
        self.name: str = _name
        self.size: int = _size
        self.ticks: int = max(0, min(_size, _ticks))

    def tick(self, _ticks=1):
        self.ticks = min(self.size, _ticks + self.ticks)
        self.ticks = max(self.ticks, 0)
        return self

    def __str__(self):
        return f'**{self.name}**: {{{self.ticks}/{self.size}}}'


def get_clock_image(clock: Clock) -> File:
    if clock.size not in clock_files_dic:
        raise NoClockImageException("clocks of this size cannot be printed, missing files")
    return File(clock_files_dic[clock.size][clock.ticks])


def get_clock_asset_folder_path():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, clocks_rel_asset_folder_path)


def load_clock_image_files():
    if not exists(get_clock_asset_folder_path()):
        logger.error("Clock asset directory path given is invalid. Check if the correct path was assigned")
        return
    clock_folders_list = os.listdir(get_clock_asset_folder_path())
    for clock_folder in clock_folders_list:
        load_single_clock_image_files(clock_folder)


def load_single_clock_image_files(clock_folder: str):
    clock_size = int(clock_folder)
    clock_sub_files_dic = {}
    for tick in range(0, clock_size + 1):
        file_name = str(clock_size) + "-" + str(tick) + ".png"
        file_name_2 = str(clock_size) + "-" + str(tick) + ".jpg"
        file_path = get_clock_asset_folder_path() + os.sep.join([clock_folder, file_name])
        file_path_2 = get_clock_asset_folder_path() + os.sep.join([clock_folder, file_name_2])
        if exists(file_path):
            clock_sub_files_dic[tick] = file_path
        elif exists(file_path_2):
            clock_sub_files_dic[tick] = file_path_2
        else:
            logger.info(f"Clock {clock_size} is missing files and has been deactivated")
            break
    if len(clock_sub_files_dic) == clock_size + 1:
        clock_files_dic[clock_size] = clock_sub_files_dic
        logger.info("clock " + str(clock_size) + " loaded and working")
