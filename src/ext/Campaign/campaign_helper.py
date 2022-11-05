from dotenv import load_dotenv
import json
import os
from os import mkdir
from os.path import exists
from datetime import datetime

from discord import File
from discord.ext.bridge import BridgeExtContext

from . import packg_variables as p_vars
from .Character import char_from_data
from .packg_variables import charDic, imported_dic
from .campaign_exceptions import CommandException

from src import GlobalVariables

save_file_no_suff = ""
saves_location_relative_to_base = 'saves'
cache_location_relative_to_base = 'saves/cache'
save_files_suffix = '_save.json'
save_type_version = '1.0'
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


def check_file_admin(ctx: BridgeExtContext) -> bool:
    if p_vars.bot_admin_id is None:
        return True
    else:
        return ctx.author.id == p_vars.bot_admin_id


def check_bot_admin(ctx: BridgeExtContext) -> bool:
    if p_vars.bot_admin_id is None:
        return True
    else:
        return ctx.author.id == p_vars.bot_admin_id


def get_bot():
    if GlobalVariables.bot is not None:
        return GlobalVariables.bot
    else:
        raise CommandException("get_bot tries to get an empty bot")


def check_if_user_has_char(user_id) -> bool:
    for char in charDic.values():
        if char.player == str(user_id):
            return True
    return False


def get_char_name_by_id(user_id: int):
    if not check_if_user_has_char(user_id):
        raise CommandException("get_char_name_by_id: attempted to get the character of an unassigned user")
    for char in charDic.values():
        if char.player == str(user_id):
            return char.name


def get_char_name_if_none(ctx: BridgeExtContext, char_name: str = None):
    if char_name is not None:
        return char_name

    for char in charDic.values():
        if char.player == str(ctx.author.id):
            return char.name
    raise CommandException(
        "No character is assigned to you. Either claim a character or add the char_name as a parameter")


def get_save_file_name_no_suff():
    return save_file_no_suff


def get_save_file_name():
    global save_file_no_suff, save_files_suffix
    return save_file_no_suff + save_files_suffix


def get_file():
    if not exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        return None
    return File(saves_location_relative_to_base + '/' + get_save_file_name())


def get_save_filepath():
    if not exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        return None
    return saves_location_relative_to_base + '/' + get_save_file_name()




def check_file_loaded(raise_error: bool = False):
    """
    Checks if a save file is currently open
    :param raise_error: If true, the function will throw a NoSaveFileException if there is no currently selected file
    :return: True if character was found, False otherwise
    """
    if get_save_file_name_no_suff() != "":
        return True
    elif raise_error:
        raise NoSaveFileException()
    else:
        return False


def check_char_name(char_name: str, raise_error: bool = False):
    """
    Checks if a character of this name exists in the current save file
    :param char_name: Name of checked character
    :param raise_error: If true, the function will throw a CommandException if the character was not found
    :return: True if character was found, False otherwise
    """
    if char_name in charDic.keys():
        return True
    elif raise_error:
        raise CommandException("Character doesn't exist")
    else:
        return False


def rename_char(char_name_old: str, char_name_new: str):
    check_file_loaded(raise_error=True)
    check_char_name(char_name_old, raise_error=True)
    if check_char_name(char_name_new):
        raise CommandException("A Character of this name already exists")

    charDic[char_name_new] = charDic[char_name_old]
    charDic[char_name_new].name = char_name_new
    del charDic[char_name_old]
    save()


def parse_date_time(time_string: str) -> datetime:
    return datetime.strptime(time_string, date_time_save_format)


def check_base_setup():
    def check_env_var_int(environment_tag: str) -> int:
        """
        This is a wrapper for environ.get, that returns an int with None instead of ""
        if the tag was written down but not assigned.

        :param environment_tag: the tag used in the environment file
        :return: returns the value if assigned, otherwise None
        """
        if os.environ.get(environment_tag) == "":
            return None
        elif os.environ.get(environment_tag) is None:
            return None
        else:
            return int(os.environ.get(environment_tag))

    load_dotenv(p_vars.campaign_dotenv_filepath)
    p_vars.cache_folder = check_env_var_int("CLOUD_SAVE_CHANNEL")
    p_vars.bot_admin_id = check_env_var_int("ADMIN_ID")
    if p_vars.bot_admin_id is None:
        input(
            "\nERROR:CAMPAIGN_EXTENSION: No admin assigned\n"
            "Restart the bot after assigning an administrator in the .env file\npress ENTER"
        )
        return

    if not exists(saves_location_relative_to_base):
        mkdir(saves_location_relative_to_base)
    if not exists(cache_location_relative_to_base):
        mkdir(cache_location_relative_to_base)


def compare_savefile_date(path1, path2):
    first_time = parse_date_time(json.load(open(path1))[last_changed_tag])
    second_time = parse_date_time(json.load(open(path2))[last_changed_tag])
    if first_time < second_time:
        return -1
    elif first_time == second_time:
        return 0
    else:
        return 1


def load(_save_name):
    global save_file_no_suff
    save_file_no_suff = _save_name
    charDic.clear()
    imported_dic.clear()
    imported_dic[session_tag] = 1
    if exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        file_dic = json.load(open(saves_location_relative_to_base + '/' + get_save_file_name()))
        if version_tag not in file_dic:
            for char_name, char_data in file_dic.items():
                charDic[char_name] = char_from_data(char_data)
        else:
            imported_dic[last_changed_tag] = parse_date_time(file_dic[last_changed_tag])
            imported_dic[session_tag] = file_dic[session_tag]
            for char_name, char_data in file_dic[character_tag].items():
                charDic[char_name] = char_from_data(char_data)
        return "Savefile exists.\nLoaded " + _save_name + "."
    else:
        return "SaveFile " + _save_name + " does not exist. SaveFile will be created when a character is added"


def save():
    if get_save_file_name_no_suff() == "":
        raise Exception("trying to save Characters without a given save_file_name")
    if not exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        print("created savefile " + get_save_file_name())
    with open(saves_location_relative_to_base + '/' + get_save_file_name(), 'w') as newfile:
        output = {
            session_tag: imported_dic[session_tag],
            last_changed_tag: datetime.now().strftime(date_time_save_format),
            version_tag: save_type_version,
            character_tag: {}
        }
        for char in charDic.values():
            temp = char.to_json()
            output[character_tag][temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)
