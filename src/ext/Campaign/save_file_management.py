import json
import logging
import os
import pathlib
from datetime import datetime
from os.path import exists
from discord import File
from . import packg_variables as p_vars
from .Character import Character
from .campaign_exceptions import CommandException


save_files_suffix = '_save.json'
save_type_version = '1.1'
date_time_save_format = "%Y-%m-%d %H:%M:%S"
character_tag = 'characters'
last_changed_tag = 'last_change'
version_tag = 'v'
session_tag = 'session'
players_tag = 'players'

logger = logging.getLogger('bot')


class SaveFileNotFoundException(CommandException):
    def __init__(self):
        super("The savefile was unexpectedly deleted")


def get_save_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, p_vars.saves_location_relative_to_module)


def get_cache_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, p_vars.cache_location_relative_to_module)


def get_savefile_path(_save_file_name):
    global save_files_suffix
    return os.sep.join([get_save_folder_filepath(), _save_file_name + save_files_suffix])


def get_savefile_as_discord_file(_save_name):
    if not exists(get_savefile_path(_save_name)):
        return None
    return File(get_savefile_path(_save_name))


def check_savefile_existence(_save_name):
    global save_files_suffix
    return exists(get_savefile_path(_save_name))


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
    with open(path1) as file1:
        path1_dic = json.load(file1)
    with open(path2) as file2:
        path2_dic = json.load(file2)

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


def load_file(_save_name):
    """
    Loads the save file with the given name from the hard drive. Raises a SaveFileNotFoundException if a file by that name cannot be found
    :param _save_name:
    :return:
    """

    save_path = get_savefile_path(_save_name)
    # file was deleted while a user was accessing it
    if not exists(save_path):
        raise SaveFileNotFoundException()

    with open(save_path) as file:
        save_dic = json.load(file)

    returned_dic = {}
    updated, save_dic = check_file_version_and_upgrade(save_dic)
    returned_dic[last_changed_tag] = parse_date_time(save_dic[last_changed_tag])
    returned_dic[session_tag] = save_dic[session_tag]
    returned_dic[character_tag] = {}
    for char_tag, char_data in save_dic[character_tag].items():
        returned_dic[character_tag][char_tag] = char_from_data(char_data)
    if updated:
        save_data_to_file(_save_name)
        logger.info(f"Old save exists.\nLoaded {_save_name} into memory and updated to newest version.")
    logger.info(f"Savefile exists.\nLoaded {_save_name} into memory.")
    return returned_dic


def save_data_to_file(_save_name: str, export_dic: dict):

    save_path = get_savefile_path(_save_name)
    if not exists(save_path):
        logger.info("created savefile " + _save_name)

    with open(save_path, 'w') as newfile:
        change_time = datetime.now().replace(microsecond=0)
        export_dic[last_changed_tag] = change_time
        print(f"new time {change_time}")
        output = {
            session_tag: export_dic[session_tag],
            last_changed_tag: change_time.strftime(date_time_save_format),
            version_tag: save_type_version,
            character_tag: {}
        }
        for char in export_dic[character_tag].values():
            temp = char.to_json()
            output[character_tag][temp['tag']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)





def remove_file(_save_name):
    if _save_name == "":
        raise Exception("cannot remove file with empty name")
    path = get_savefile_path(_save_name)
    del file_dic[_save_name]
    if exists(path):
        logger.info("deleted savefile", _save_name)
        os.remove(path)
