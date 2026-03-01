import json
import logging
import os
from datetime import datetime
from os.path import exists
from os import mkdir
from discord import File
from ..Character import Character
from ..campaign_exceptions import SaveFileNotFoundException
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
    """
    Initializes the folders needed for the save system to work correctly
    """
    if not exists(get_save_folder_filepath()):
        logger.debug("SAVE_FILEPATH_CREATED")
        mkdir(get_save_folder_filepath())
    if not exists(get_cache_folder_filepath()):
        logger.debug("CACHE_FILEPATH_CREATED")
        mkdir(get_cache_folder_filepath())


def get_savefile_as_discord_file(_save_name) -> File:
    """
    Gets a File object pointing to a save_file on the hard drive

    :param _save_name: the save_file name without suffix
    :return: The file object
    :raises SaveFileNotFoundException: if file by the given name is not found
    """

    file_path = build_savefile_path(_save_name)
    if not exists(file_path):
        raise SaveFileNotFoundException()
    return File(file_path)


def check_savefile_existence(_save_name) -> bool:
    """
    Checks if save_file of given name exists on the hard drive

    :param _save_name: the save_file name without suffix
    :return: True if save_file exists, False otherwise
    """
    return exists(build_savefile_path(_save_name))


def remove_save_file(_save_name) -> None:
    """
    Removes the save_file with the given name from the hard drive

    :param _save_name: The name of the save_file without suffix
    :raises Exception: If save_file cannot be found
    """
    if _save_name == "":
        raise Exception("cannot remove file with empty name")
    path = build_savefile_path(_save_name)
    if exists(path):
        logger.info("deleted savefile", _save_name)
        os.remove(path)


def compare_savefile_novelty_by_path(path1: str, path2: str) -> int:
    """
    Compares two save_files on the hard drive via their respective paths.

    :param path1: path of the first file
    :param path2: path of the second file
    :return: -1 if path1 is older, 0 if they are the same, 1 if path2 is older
    """
    if not exists(path1) or not exists(path2):
        raise Exception(f"cannot compare files that don't exist: \npath1: {path1} \npath2: {path2}")
    with open(path1) as file1:
        path1_dic = json.load(file1)
    with open(path2) as file2:
        path2_dic = json.load(file2)

    return compare_unparsed_dict_novelty(path1_dic, path2_dic)


def save_file_to_parsed_dictionary(_save_name) -> dict:
    """
    Loads the save file with the given name from the hard drive, parses it, and updates
    it to the newest save_file version if necessary.

    :param _save_name: the name of the save file to be loaded
    :return: the parsed save_file dictionary
    :raises SaveFileNotFoundException: if a file by given name does not exist on the hard drive
    """
    updated, save_dict = check_file_version_and_update(save_file_to_unparsed_dict(_save_name))
    returned_dict = {}
    for key, value in save_dict.items():
        returned_dict[key] = value
    returned_dict[last_changed_tag] = str_to_datetime(save_dict[last_changed_tag])
    returned_dict[character_tag] = {}
    for char_tag, char_data in save_dict[character_tag].items():
        returned_dict[character_tag][char_tag] = json_dict_to_character(char_data)
    if updated:
        save_data_to_file(_save_name, returned_dict)
        logger.info(f"Updated {_save_name} to newest version and loaded into memory.")
    return returned_dict


def save_file_to_unparsed_dict(_save_name) -> dict:
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
        output = create_fresh_save(export_dic[admin_tag])
        output[session_tag] = export_dic[session_tag]
        output[last_changed_tag] = change_time.strftime(date_time_save_format)
        output[players_tag] = export_dic[players_tag]
        for char in export_dic[character_tag].values():
            temp = char.__dict__
            output[character_tag][temp['tag']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)
        if created:
            logger.info("created savefile " + _save_name)


def json_dict_to_character(char_dic: dict) -> Character:
    """
    Turns a json dictionary loaded from a savefile into a Character object

    :param char_dic: the loaded dictionary containing infos of a single character
    :return: The created character object
    """
    char = Character("debug", "debug")
    for key, value in char_dic.items():
        char.__dict__[key] = value
    return char


def str_to_datetime(time_string: str) -> datetime:
    """
    Converts a string into datetime object, according to the format outlined in the save_file_management file
    :param time_string: the string to be converted
    :return: datetime object
    """
    return datetime.strptime(time_string, date_time_save_format)


def character_from_save_file(_save_name, _char_tag) -> Character:
    """
    Should only be used during testing:

    Opens a save_file and returns the character with the given tag as a Character object

    :param _save_name: save_file name without suffix
    :param _char_tag: tag of character
    :return: the loaded Character object
    """
    file_dict = save_file_to_parsed_dictionary(_save_name)
    if _char_tag not in file_dict[character_tag]:
        raise Exception("Character not in this savefile")
    return file_dict[character_tag][_char_tag]


def create_fresh_save(admin: str = "") -> dict:
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
        fresh_save = create_fresh_save()
        for key in save_file_data.keys():
            fresh_save[key] = save_file_data[key]

    return True, fresh_save


def compare_unparsed_dict_novelty(dic1: dict, dic2: dict) -> int:
    """
    Compares which unparsed json-file dictionary is the more recently updated one. It first compares savefile version, then the last-changed timestamp

    :param dic1: The first unparsed json dictionary
    :param dic2: The second unparsed json dictionary
    :return: -1 if dic1 is older, 0 if they are the same, 1 if dic2 is older
    """
    first_time = str_to_datetime(dic1[last_changed_tag])
    second_time = str_to_datetime(dic2[last_changed_tag])
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
