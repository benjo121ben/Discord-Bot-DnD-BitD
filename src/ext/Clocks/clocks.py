import logging
from os.path import exists
from discord import File
import os
import json
from json.decoder import JSONDecodeError
import pathlib


clock_files_dic = {}
clocks_rel_asset_folder_path = os.sep.join(['Assets', ''])
clocks_rel_save_path = os.sep.join(['..', '..', '..', 'saves', 'clock_saves'])
clock_save_suffix = '_clsave.json'
logger = logging.getLogger('bot')


class NoClockImageException(Exception):
    pass


class Clock:
    def __init__(self, _tag: str, _name: str, _size: int, _ticks: int = 0):
        self.tag: str = _tag
        self.name: str = _name
        self.size: int = _size
        self.ticks: int = max(0, min(_size, _ticks))

    def tick(self, _ticks=1):
        self.ticks = min(self.size, _ticks + self.ticks)
        self.ticks = max(self.ticks, 0)
        return self

    def assign_dic(self, dictionary):
        self.__dict__ = dictionary
        return self

    def __str__(self):
        return f'**{self.name}**/Tag:_{self.tag}_: {{{self.ticks}/{self.size}}}'


def get_clock_image(clock: Clock) -> File:
    if clock.size not in clock_files_dic:
        raise NoClockImageException("clocks of this size cannot be printed, missing files")
    return File(clock_files_dic[clock.size][clock.ticks])


def clock_from_json(clock_data):
    return Clock("TEMP", "TEMP_NAME", 4).assign_dic(clock_data)


def get_clock_save_filepath(user_id: str):
    global clocks_rel_save_path, clock_save_suffix
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, os.sep.join([clocks_rel_save_path, user_id + clock_save_suffix]))


def get_clock_asset_folder_path():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, clocks_rel_asset_folder_path)


def load_clocks(user_id: str):
    clocks_save_dic = {}
    if exists(get_clock_save_filepath(user_id)):
        with open(get_clock_save_filepath(user_id)) as file:
            try:
                imported_dic = json.load(file)
            except JSONDecodeError as e:
                logger.error(str(e))
                logger.error(f"user_id: {user_id}")
                raise Exception("An error has occured trying to parse JSON clock file")
        for clock_data in imported_dic.values():
            clocks_save_dic[clock_data["tag"]] = clock_from_json(clock_data)
        return clocks_save_dic
    else:
        logger.info(f"Clock savefile doesn't exist, will create new savefile. User ID={user_id}")
        return {}


def save_clocks(user_id: str, clocks_save_dic: dict):
    if len(clocks_save_dic) == 0:
        if exists(get_clock_save_filepath(user_id)):
            os.remove(get_clock_save_filepath(user_id))
        return

    if not exists(get_clock_save_filepath(user_id)):
        path = ""
        for path_part in get_clock_save_filepath(user_id).split(os.sep):
            path += path_part + os.sep
            if not exists(path) and ".json" not in path:
                os.mkdir(path)
        logger.info("created savefile")
    with open(get_clock_save_filepath(user_id), 'w') as newfile:
        output = {}
        for clock in clocks_save_dic.values():
            output[clock.tag] = clock.__dict__
        json.dump(output, newfile, sort_keys=True, indent=4)


def load_clock_files():
    if not exists(get_clock_asset_folder_path()):
        logger.error("Clock asset directory path given is invalid. Check if the correct path was assigned")
        return
    clock_folders_list = os.listdir(get_clock_asset_folder_path())
    for clock_folder in clock_folders_list:
        load_single_clock_files(clock_folder)


def load_single_clock_files(clock_folder: str):
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
