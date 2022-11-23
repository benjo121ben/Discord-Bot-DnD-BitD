import json
import os
import pathlib
from datetime import datetime
from os.path import exists

from discord import File

from .import packg_variables as p_vars
from .Character import Character
from .campaign_exceptions import CommandException
from .packg_variables import charDic, imported_dic


save_file_no_suffix = ""
save_files_suffix = '_save.json'
save_type_version = '1.1'
date_time_save_format = "%Y-%m-%d %H:%M:%S"
character_tag = 'characters'
last_changed_tag = 'last_change'
version_tag = 'v'
session_tag = 'session'


class NoSaveFileException(CommandException):
    def __init__(self):
        super(CommandException, self).__init__(
            "No savefile has been loaded. Use the file command to load an existing file or create a new one"
        )


def get_current_save_file_name_no_suff():
    return save_file_no_suffix


def get_current_save_file_name():
    global save_file_no_suffix, save_files_suffix
    return save_file_no_suffix + save_files_suffix


def get_current_savefile_as_discord_file():
    if not exists(get_current_savefile_path()):
        return None
    return File(get_current_savefile_path())


def get_save_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, p_vars.saves_location_relative_to_module)


def get_cache_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, p_vars.cache_location_relative_to_module)


def get_current_savefile_path():
    return get_save_folder_filepath() + f'{os.sep}' + get_current_save_file_name()


def check_file_loaded(raise_error: bool = False):
    """
    Checks if a save file is currently open
    :param raise_error: If true, the function will throw a NoSaveFileException if there is no currently selected file
    :return: True if character was found, False otherwise
    """
    if get_current_save_file_name_no_suff() != "":
        return True
    elif raise_error:
        raise NoSaveFileException()
    else:
        return False


def check_file_version_and_upgrade(save_file_data) -> (bool, dict):
    global save_type_version, version_tag, character_tag, last_changed_tag, session_tag
    if version_tag in save_file_data and save_file_data[version_tag] == save_type_version:
        return False, save_file_data
    else:
        imported_char_dic = None
        if version_tag not in save_file_data:
            imported_char_dic = save_file_data
            save_file_data = {version_tag: save_type_version, last_changed_tag: "0001-01-01 00:00:00"}
        else:
            imported_char_dic = save_file_data[character_tag]
        if session_tag not in save_file_data:
            save_file_data[session_tag] = 1
        for _, char_data in imported_char_dic.items():
            if 'crits' not in char_data:
                char_data['crits'] = 0
                char_data['faints'] = 0
                char_data['kills'] = 0
            if 'dodged' not in char_data:
                char_data['dodged'] = 0
            if 'tag' not in char_data:
                char_data['tag'] = char_data['name']
        save_file_data[character_tag] = imported_char_dic
    return True, save_file_data


def char_from_data(data):
    char = Character(data['tag'], data['name'], data['max_health'])
    char.__dict__ = data
    return char


def parse_date_time(time_string: str) -> datetime:
    return datetime.strptime(time_string, date_time_save_format)


def compare_savefile_novelty(path1, path2):
    path1_dic = json.load(open(path1))
    first_time = parse_date_time(path1_dic[last_changed_tag])
    first_version = float(path1_dic[version_tag])
    path2_dic = json.load(open(path2))
    second_time = parse_date_time(path2_dic[last_changed_tag])
    second_version = float(path2_dic[version_tag])
    if first_version < second_version or first_time < second_time:
        return -1
    elif first_version == second_version or first_time == second_time:
        return 0
    else:
        return 1


def load(_save_name):
    global save_file_no_suffix
    save_file_no_suffix = _save_name
    charDic.clear()
    imported_dic.clear()
    imported_dic[session_tag] = 1
    if exists(get_current_savefile_path()):
        file_dic = json.load(open(get_current_savefile_path()))
        updated, file_dic = check_file_version_and_upgrade(file_dic)
        imported_dic[last_changed_tag] = parse_date_time(file_dic[last_changed_tag])
        imported_dic[session_tag] = file_dic[session_tag]
        for char_tag, char_data in file_dic[character_tag].items():
            charDic[char_tag] = char_from_data(char_data)
        if updated:
            save()
            return "Savefile of older version exists.\nLoaded " + _save_name + " and updated to newest version."
        return "Savefile exists.\nLoaded " + _save_name + "."
    else:
        return "SaveFile " + _save_name + " does not exist. SaveFile will be created when a character is added"


def save():
    if get_current_save_file_name_no_suff() == "":
        raise Exception("trying to save Characters without a given save_file_name")
    if not exists(get_current_savefile_path()):
        print("created savefile " + get_current_save_file_name())
    with open(get_current_savefile_path(), 'w') as newfile:
        output = {
            session_tag: imported_dic[session_tag],
            last_changed_tag: datetime.now().strftime(date_time_save_format),
            version_tag: save_type_version,
            character_tag: {}
        }
        for char in charDic.values():
            temp = char.to_json()
            output[character_tag][temp['tag']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)
