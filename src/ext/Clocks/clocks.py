from os.path import exists
from discord import File
import os
import json
import pathlib


clock_files_dic = {}
clocks_rel_asset_folder_path = os.sep.join(['..', '..', '..', 'Assets', 'Clocks', ''])
clocks_rel_save_path = os.sep.join(['..', '..', '..', 'saves', 'clock_saves.json'])


class NoClockImageException(Exception):
    pass


class Clock:
    def __init__(self, _name: str, _size: int, _ticks: int = 0):
        self.name: str = _name
        self.size: int = _size
        self.existing_ticks: int = max(0, min(_size, _ticks))

    def tick(self, _ticks=1):
        self.existing_ticks = min(self.size,  _ticks + self.existing_ticks)
        self.existing_ticks = max(self.existing_ticks, 0)
        return self

    def assign_dic(self, dictionary):
        self.__dict__ = dictionary
        return self

    def __str__(self):
        return self.name + " Clock:{" + str(self.existing_ticks) + "/" + str(self.size) + "}"

    def get_embed_info(self) -> (str, File):
        if not self.size in clock_files_dic:
            raise NoClockImageException("clocks of this size cannot be printed, missing files")
        return self.name, File(clock_files_dic[self.size][self.existing_ticks])


clocks_save_dic: dict[str, Clock] = {}


def clock_from_json(clock_data):
    return Clock("TEMP", 4).assign_dic(clock_data)


def get_clock_save_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, clocks_rel_save_path)


def get_clock_asset_folder_path():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, clocks_rel_asset_folder_path)


def load_clocks():
    if exists(get_clock_save_filepath()):
        print("Clocks savefile exists")
        with open(get_clock_save_filepath()) as file:
            imported_dic = json.load(file)
        for clock_data in imported_dic.values():
            clocks_save_dic[clock_data["name"]] = clock_from_json(clock_data)
    else:
        print("Clock savefile doesn't exist, will create new savefile")
    load_clock_files()


def save_clocks():
    if not exists(get_clock_save_filepath()):
        path = ""
        for path_part in get_clock_save_filepath().split(os.sep):
            path += path_part + os.sep
            if not exists(path) and not ".json" in path:
                os.mkdir(path)
        print("created savefile")
    with open(get_clock_save_filepath(), 'w') as newfile:
        output = {}
        for clock in clocks_save_dic.values():
            output[clock.name] = clock.__dict__
        json.dump(output, newfile, sort_keys=True, indent=4)


def load_clock_files():
    if not exists(get_clock_asset_folder_path()):
        print("No clock file directory")
        return
    clock_folders_list = os.listdir(get_clock_asset_folder_path())
    for clock_folder in clock_folders_list:
        load_single_clock_files(clock_folder)


def load_single_clock_files(clock_folder : str):
    clock_size = int(clock_folder)
    clock_sub_files_dic = {}
    for tick in range(0, clock_size + 1):
        file_name = str(clock_size) + "-" + str(tick) + ".png"
        file_path = get_clock_asset_folder_path() + os.sep.join([clock_folder, file_name])
        if exists(file_path):
            clock_sub_files_dic[tick] = file_path
        else:
            print("Clock " + str(clock_size) + " is missing files and has been deactivated")
            break
    if len(clock_sub_files_dic) == clock_size + 1:
        clock_files_dic[clock_size] = clock_sub_files_dic
        print("clock " + str(clock_size) + " loaded")




