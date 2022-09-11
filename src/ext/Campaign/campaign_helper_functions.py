from .packg_variables import charDic
from ..command_exceptions import *
from os.path import exists
from os import mkdir
from .Character import char_from_data
import json
from discord import File

save_file_name = ""


def get_file():
    if not exists('saves/' + save_file_name):
        return None
    return File('saves/' + save_file_name)


def get_setup_file_name():
    global save_file_name
    if save_file_name == "":
        print("Input savefile used")
        save_file_name = input() + "_save.json"
    load(save_file_name)


def load(_save_name):
    global save_file_name
    save_file_name = _save_name
    if exists('saves/' + _save_name):
        print("Savefile exists")
        print("Loaded " + _save_name)
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


# is there to avoid functions being called on a character that doesn't exist
def check_char_name(char_name):
    if char_name in charDic.keys():
        return True
    else:
        raise CommandException("Character doesn't exist")
