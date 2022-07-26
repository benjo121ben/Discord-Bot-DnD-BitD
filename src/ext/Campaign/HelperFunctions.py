from .packg_variables import charDic
from ..command_exceptions import *
from os.path import exists
from os import mkdir
from .Character import char_from_data
import json

save_file_name = ""


def get_save_file():
    global save_file_name
    print("Input savefile used")
    load(input() + "_save.json")


def load(_save_name):
    global save_file_name
    save_file_name = _save_name
    if exists('saves/' + _save_name):
        print("Savefile exists")
        imported_dic = json.load(open('saves/' + _save_name))
        for char_name, char_data in imported_dic.items():
            charDic[char_name] = char_from_data(char_data)


def save():
    global save_file_name
    if save_file_name == "":
        raise Exception("trying to save Characters without a given save_file_name")
    if not exists('saves/' + save_file_name):
        if not exists('saves'):
            mkdir("saves")
        print("created savefile")
    with open('saves/' + save_file_name, 'w') as newfile:
        output = {}
        for char in charDic.values():
            temp = char.to_json()
            output[temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)


def check_min_command_arg_len(min: int, *args, throw_error=True):
    return check_contained_command_arg_len(min, -1, *args, throw_error)


# This checks in case of missing parameters or invalid amounts. does not cover multiple versions of same Command
def check_contained_command_arg_len(min: int, max: int, *args, throw_error=True):
    if max != -1 and len(args) > max:
        if throw_error:
            raise TooManyArgumentsException(max)
    elif len(args) < min:
            return False
    return True


# is there to avoid functions being called on a character that doesn't exist
def check_char_name(char_name):
    if char_name in charDic.keys():
        return True
    else:
        raise CommandException("Character doesn't exist")
