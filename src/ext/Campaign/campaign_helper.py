import json
from os import mkdir
from os.path import exists

from discord import File
from discord.ext.bridge import BridgeExtContext

from .Character import char_from_data
from .packg_variables import charDic
from ..command_exceptions import *

save_file_name = ""
saves_location_relative_to_base = 'saves'
save_files_suffix = '_save.json'


class NoSaveFileException(CommandException):
    def __init__(self):
        message = "No savefile has been loaded. Use the file command to load an existing file or create a new one"
        super(CommandException, self).__init__(message)


def check_if_user_has_char(user_id: str) -> bool:
    for char in charDic.values():
        if char.player == user_id:
            return True
    return False


def get_char_name_if_none(char_name: str, ctx: BridgeExtContext):
    if char_name is not None:
        return char_name

    for char in charDic.values():
        if char.player == str(ctx.author.id):
            return char.name
    raise CommandException("No character is assigned to you. Either claim a character or add the char_name as a parameter")


def get_save_file_name():
    return save_file_name


def get_file():
    if not exists(saves_location_relative_to_base + '/' + save_file_name):
        return None
    return File(saves_location_relative_to_base + '/' + save_file_name)


def check_file_loaded(raise_error: bool = False):
    """
    Checks if a save file is currently open
    :param raise_error: If true, the function will throw a NoSaveFileException if there is no currently selected file
    :return: True if character was found, False otherwise
    """
    global save_file_name
    if save_file_name != "":
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


def load(_save_name):
    global save_file_name
    save_file_name = _save_name + save_files_suffix
    charDic.clear()
    if exists(saves_location_relative_to_base + '/' + save_file_name):
        imported_dic = json.load(open(saves_location_relative_to_base + '/' + save_file_name))
        for char_name, char_data in imported_dic.items():
            charDic[char_name] = char_from_data(char_data)
        return "Savefile exists.\nLoaded " + _save_name + "."

    else:
        return "SaveFile " + _save_name + " does not exist. SaveFile will be created when a character is added"


def save():
    global save_file_name
    if save_file_name == "":
        raise Exception("trying to save Characters without a given save_file_name")
    if not exists(saves_location_relative_to_base + '/' + save_file_name):
        if not exists(saves_location_relative_to_base):
            mkdir(saves_location_relative_to_base)
        print("created savefile" + save_file_name)
    with open(saves_location_relative_to_base + '/' + save_file_name, 'w') as newfile:
        output = {}
        for char in charDic.values():
            temp = char.to_json()
            output[temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)



