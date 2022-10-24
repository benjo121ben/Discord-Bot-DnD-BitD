import json
from os import mkdir
from os.path import exists

from discord import File
from discord.ext.bridge import BridgeExtContext

from .Character import char_from_data
from .packg_variables import charDic
from ..command_exceptions import *

save_file_no_suff = ""
saves_location_relative_to_base = 'saves'
save_files_suffix = '_save.json'


class NoSaveFileException(CommandException):
    def __init__(self):
        message = "No savefile has been loaded. Use the file command to load an existing file or create a new one"
        super(CommandException, self).__init__(message)


def check_if_user_has_char(user_id) -> bool:
    for char in charDic.values():
        if char.player == str(user_id):
            return True
    return False


def get_char_name_if_none(char_name: str, ctx: BridgeExtContext):
    if char_name is not None:
        return char_name

    for char in charDic.values():
        if char.player == str(ctx.author.id):
            return char.name
    raise CommandException("No character is assigned to you. Either claim a character or add the char_name as a parameter")


def get_save_file_name_no_suff():
    return save_file_no_suff


def get_save_file_name():
    global save_file_no_suff, save_files_suffix
    return save_file_no_suff + save_files_suffix


def get_file():
    if not exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        return None
    return File(saves_location_relative_to_base + '/' + get_save_file_name())


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


def load(_save_name):
    global save_file_no_suff
    save_file_no_suff = _save_name
    charDic.clear()
    if exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        imported_dic = json.load(open(saves_location_relative_to_base + '/' + get_save_file_name()))
        for char_name, char_data in imported_dic.items():
            charDic[char_name] = char_from_data(char_data)
        return "Savefile exists.\nLoaded " + _save_name + "."

    else:
        return "SaveFile " + _save_name + " does not exist. SaveFile will be created when a character is added"


def save():
    if get_save_file_name_no_suff() == "":
        raise Exception("trying to save Characters without a given save_file_name")
    if not exists(saves_location_relative_to_base + '/' + get_save_file_name()):
        if not exists(saves_location_relative_to_base):
            mkdir(saves_location_relative_to_base)
        print("created savefile " + get_save_file_name())
    with open(saves_location_relative_to_base + '/' + get_save_file_name(), 'w') as newfile:
        output = {}
        for char in charDic.values():
            temp = char.to_json()
            output[temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)



