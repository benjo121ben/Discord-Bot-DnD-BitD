from src.Character import *
from os.path import exists
from src import Commands, GlobalVariables
import json
import os


def load(_save_name):
    if exists('saves/' + _save_name):
        print("Savefile exists")
        imported_dic = json.load(open('saves/' + _save_name))
        for char_name, char_data in imported_dic.items():
            GlobalVariables.charDic[char_name] = char_from_data(char_data)


def save(_save_name):
    if not exists('saves/' + _save_name):
        if not exists('saves'):
            os.mkdir("saves")
        print("created savefile")
    with open('saves/' + _save_name, 'w') as newfile:
        output = {}
        for char in GlobalVariables.charDic.values():
            temp = toJSON(char)
            output[temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)


def input_loop(_save_name, _available_commands):
    print("current characters:")
    _names = ", ".join(GlobalVariables.charDic.keys())
    print(_names)
    print("input command: " + _available_commands)
    _passed_args = input().split(' ')
    print()
    if _passed_args[0] == 'q':
        exit()
    Commands.execute_command(*_passed_args)
    save(_save_name)
    print()
    print("-----------------------------")


def main():
    print("Input savefile name")
    _save_name = input() + "_save.json"
    load(_save_name)
    _available_commands = ", ".join(Commands.localCommDic.keys())
    print("---setup-complete---")
    while True:
        input_loop(_save_name, _available_commands)


main()
