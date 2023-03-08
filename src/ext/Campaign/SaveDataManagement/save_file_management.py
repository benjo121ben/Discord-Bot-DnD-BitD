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

save_files_suffix = '_save.json'
save_type_version = 1.3
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
    if not exists(build_savefile_path(_save_name)):
        return None
    return File(build_savefile_path(_save_name))


def check_savefile_existence(_save_name):
    global save_files_suffix
    return exists(build_savefile_path(_save_name))


def remove_file(_save_name):
    if _save_name == "":
        raise Exception("cannot remove file with empty name")
    path = build_savefile_path(_save_name)
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
    """Loads the save file with the given name from the hard drive.
    Raises a SaveFileNotFoundException if a file by that name cannot be found.

    :param _save_name: the name of the save file to be loaded
    :return: the interpreted save file dictionary
    """
    updated, save_dict = check_file_version_and_update(get_file_json_dict(_save_name))
    returned_dict = {}
    for key, value in save_dict.items():
        returned_dict[key] = value
    returned_dict[last_changed_tag] = parse_date_time(save_dict[last_changed_tag])
    returned_dict[character_tag] = {}
    for char_tag, char_data in save_dict[character_tag].items():
        returned_dict[character_tag][char_tag] = char_from_data(char_data)
    if updated:
        save_data_to_file(_save_name, returned_dict)
        logger.info(f"Updated {_save_name} to newest version and loaded into memory.")
    return returned_dict


def get_file_json_dict(_save_name):
    """
    Gets the pure unparsed json dictionary from a save_file

    :param _save_name: the name of the save_file without the suffix
    :return: The pure json dictionary
    :raises SaveFileNotFoundException: if a file of this name cannot be found
    """
    save_path = build_savefile_path(_save_name)
    # file was deleted while a user was accessing it
    if not exists(save_path):
        raise SaveFileNotFoundException()
    with open(save_path) as file:
        save_dic = json.load(file)
        return save_dic


def save_data_to_file(_save_name: str, export_dic: dict) -> None:
    """
    Saves the provided dictionary into a save_file on the hard_drive

    :param _save_name: the name of the save_file without the suffix, cannot be empty or None
    :param export_dic: The dictionary that should be exported, cannot be None
    :raises Exception: if either parameter is invalid
    """
    if _save_name is None or _save_name == "":
        raise Exception("A file with an empty name cannot be saved to storage")
    if export_dic is None:
        raise Exception("Trying to save an empty dictionary as a save")
    save_path = build_savefile_path(_save_name)
    created = not exists(save_path)

    with open(save_path, 'w') as newfile:
        change_time = datetime.now().replace(microsecond=0)
        export_dic[last_changed_tag] = change_time
        output = get_fresh_save(export_dic[admin_tag])
        output[session_tag] = export_dic[session_tag]
        output[last_changed_tag] = change_time.strftime(date_time_save_format)
        output[players_tag] = export_dic[players_tag]
        for char in export_dic[character_tag].values():
            temp = char.__dict__
            output[character_tag][temp['tag']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)
        if created:
            logger.info("created savefile " + _save_name)


def char_from_data(char_dic: dict) -> Character:
    """
    Turns a json dictionary loaded from a savefile into a Character object

    :param char_dic: the loaded dictionary containing infos of a single character
    :return: The created character object
    """
    char = Character("debug", "debug")
    for key, value in char_dic.items():
        char.__dict__[key] = value
    return char


def parse_date_time(time_string: str) -> datetime:
    return datetime.strptime(time_string, date_time_save_format)


def get_fresh_save(admin: str = ""):
    """
    Creates a fresh save_file dictionary associated with the given admin ID

    :param admin: the user id of the user that has admin access to the file
    :return: the created dictionary
    """
    return {
        session_tag: 1,
        last_changed_tag: datetime.now().replace(microsecond=0).strftime(date_time_save_format),
        version_tag: save_type_version,
        character_tag: {},
        admin_tag: admin,
        players_tag: [admin]
    }


def check_file_version_and_update(save_file_data: dict) -> (bool, dict):
    """
    Checks if the given save file dictionary requires an update and updates it if necessary

    :param save_file_data: The dictionary containing all infos of a single parsed json save file
    :return: tuple[bool, dict]. bool is true if the file was updated, dict is the updated dictionary
    """
    global save_type_version, version_tag
    if version_tag in save_file_data and float(save_file_data[version_tag]) >= save_type_version:
        return False, save_file_data
    else:
        fresh_save = get_fresh_save()
        for key in save_file_data.keys():
            fresh_save[key] = save_file_data[key]

    return True, fresh_save


def compare_dict_novelty(dic1: dict, dic2: dict) -> int:
    """
    Compares which unparsed json-file dictionary is the more recently updated one. It first compares savefile version, then the last-changed timestamp

    :param dic1: The first unparsed json dictionary
    :param dic2: The second unparsed json dictionary
    :return: -1 if dic1 is older, 0 if they are the same, 1 if dic1 is older
    """
    first_time = parse_date_time(dic1[last_changed_tag])
    second_time = parse_date_time(dic2[last_changed_tag])
    first_version = float(dic1[version_tag])
    second_version = float(dic2[version_tag])
    if first_version < second_version or first_time < second_time:
        return -1
    elif first_version == second_version or first_time == second_time:
        return 0
    else:
        return 1


def build_savefile_path(_save_file_name) -> str:
    """
    Builds a file path with the given save_file name, depending on the os

    :param _save_file_name: The save_file name without suffix
    :return: the built file path
    """
    global save_files_suffix
    return os.sep.join([get_save_folder_filepath(), _save_file_name + save_files_suffix])
