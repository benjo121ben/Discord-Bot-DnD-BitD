import json
import logging
import os
from datetime import datetime
from os.path import exists
from os import mkdir
from discord import File
from ..Character import Character
from ..campaign_exceptions import SaveFileNotFoundException, SaveFileImportException
from ..packg_variables import get_save_folder_filepath, get_cache_folder_filepath
from ...command_exceptions import CommandException

save_files_suffix = '_save.json'
save_type_version = '1.2'
date_time_save_format = "%Y-%m-%d %H:%M:%S"
character_tag = 'characters'
last_changed_tag = 'last_change'
version_tag = 'v'
session_tag = 'session'
players_tag = 'players'
admin_tag = 'admin'

logger = logging.getLogger('bot')


def setup_save_folders():
    if not exists(get_save_folder_filepath()):
        logger.debug("SAVE_FILEPATH_CREATED")
        mkdir(get_save_folder_filepath())
    if not exists(get_cache_folder_filepath()):
        logger.debug("CACHE_FILEPATH_CREATED")
        mkdir(get_cache_folder_filepath())


def get_savefile_as_discord_file(_save_name):
    if not exists(get_savefile_path(_save_name)):
        return None
    return File(get_savefile_path(_save_name))


def check_savefile_existence(_save_name):
    global save_files_suffix
    return exists(get_savefile_path(_save_name))


def remove_file(_save_name):
    if _save_name == "":
        raise Exception("cannot remove file with empty name")
    path = get_savefile_path(_save_name)
    if exists(path):
        logger.info("deleted savefile", _save_name)
        os.remove(path)


def compare_savefile_novelty(path1, path2):
    with open(path1) as file1:
        path1_dic = json.load(file1)
    with open(path2) as file2:
        path2_dic = json.load(file2)

    return compare_dict_novelty(path1_dic, path2_dic)


def parse_savefile_contents(_save_name):
    """
    Loads the save file with the given name from the hard drive. Raises a SaveFileNotFoundException if a file by that name cannot be found
    :param _save_name: the name of the save file to be loaded
    :return: the interpreted save file dictionary
    """

    updated, save_dict = upgrade_savefile_dict(get_file_json_dict(_save_name))
    returned_dict = {}
    for key, value in save_dict.items():
        returned_dict[key] = value
    returned_dict[last_changed_tag] = parse_date_time(save_dict[last_changed_tag])
    returned_dict[character_tag] = {}
    for char_tag, char_data in save_dict[character_tag].items():
        returned_dict[character_tag][char_tag] = char_from_data(char_data)
    if updated:
        save_data_to_file(_save_name, returned_dict)
        logger.info(f"Old save exists.\nLoaded {_save_name} into memory and updated to newest version.")
    logger.info(f"Savefile exists.\nLoaded {_save_name} into memory.")
    return returned_dict


def get_file_json_dict(_save_name):
    save_path = get_savefile_path(_save_name)
    # file was deleted while a user was accessing it
    if not exists(save_path):
        raise SaveFileNotFoundException()
    with open(save_path) as file:
        save_dic = json.load(file)
        return save_dic


def save_data_to_file(_save_name: str, export_dic: dict):
    if _save_name == "":
        raise Exception("A file with an empty name cannot be saved to storage")
    if export_dic is None:
        raise Exception("Trying to save an empty dictionary as a save")
    save_path = get_savefile_path(_save_name)
    if not exists(save_path):
        logger.info("created savefile " + _save_name)

    with open(save_path, 'w') as newfile:
        change_time = datetime.now().replace(microsecond=0)
        export_dic[last_changed_tag] = change_time
        print(f"new time {change_time}")
        output = get_fresh_save(export_dic[admin_tag])
        output[session_tag] = export_dic[session_tag]
        output[last_changed_tag] = change_time.strftime(date_time_save_format)
        output[players_tag] = export_dic[players_tag]
        for char in export_dic[character_tag].values():
            temp = char.to_json()
            output[character_tag][temp['tag']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)


def char_from_data(data: dict) -> Character:
    char = Character("debug", "debug", 0)
    for key, value in data.items():
        char.__dict__[key] = value
    for key, value in char.__dict__.items():
        if value == "debug":
            raise SaveFileImportException()
    return char


def parse_date_time(time_string: str) -> datetime:
    return datetime.strptime(time_string, date_time_save_format)


def get_fresh_save(admin: str = ""):
    return {
        session_tag: 1,
        last_changed_tag: datetime.now().replace(microsecond=0).strftime(date_time_save_format),
        version_tag: save_type_version,
        character_tag: {},
        admin_tag: admin,
        players_tag: [admin]
    }


def upgrade_savefile_dict(save_file_data: dict) -> (bool, dict):
    global save_type_version, version_tag
    if version_tag in save_file_data and save_file_data[version_tag] == save_type_version:
        return False, save_file_data
    else:
        fresh_save = get_fresh_save()
        for key in save_file_data.keys():
            fresh_save[key] = save_file_data[key]

    return True, fresh_save


def compare_dict_novelty(path1_dic: dict, path2_dic: dict):
    first_time = parse_date_time(path1_dic[last_changed_tag])
    second_time = parse_date_time(path2_dic[last_changed_tag])
    first_version = float(path1_dic[version_tag])
    second_version = float(path2_dic[version_tag])
    if first_version < second_version or first_time < second_time:
        return -1
    elif first_version == second_version or first_time == second_time:
        return 0
    else:
        return 1


def get_savefile_path(_save_file_name):
    global save_files_suffix
    return os.sep.join([get_save_folder_filepath(), _save_file_name + save_files_suffix])
