from Character import *
from os.path import exists
import json
import os


def check_command_arg_len(supposed_len, *args):
    if len(args) != supposed_len:
        print("command has invalid argunments")
        return False
    return True


def check_char_name(char_name):
    print(char_name)
    if char_name in charDic.keys():
        return True
    else:
        print("Character doesn't exist")
        return False


def log(*args):
    for char in charDic.values():
        print(char)


# command usage: addC game_name player_name char_name
def add_char(*args):
    if check_command_arg_len(3, *args):
        _player_name, _char_name, _max_health = args
        _max_health = int(args[2])
        charDic[_char_name] = Character(_player_name, _char_name,_max_health)
        print("character", _char_name, "added")


# command usage: addC game_name player_name char_name
def cause_damage(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].cause_dam(_dam)
        print("character", _char_name, "caused", _dam, "damage")


def take_damage(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].take_dam(_dam)
        print("character", _char_name, "takes", _dam, "damage")


def heal_max(*args):
    if check_command_arg_len(1, *args) and check_char_name(args[0]):
        _char_name = args[0]
        charDic[_char_name].heal_max()
        print("character", _char_name, "healed to their maximum")


def heal(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _healed = int(args[1])
        charDic[_char_name].heal_dam(_healed)
        print("character", _char_name, "healed", _healed)

def increase_health(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _health_inc = int(args[1])
        charDic[_char_name].inc_max_health(_health_inc)
        print("character", _char_name, "health increased by", _health_inc)


def change_command(*args):
    global currentComm, comm_name, localCommDic
    _command_name = args[0]
    if _command_name in localCommDic.keys():
        currentComm = localCommDic[_command_name]
        comm_name = _command_name
        print("command changed to", comm_name)
    else:
        print("invalid command change")
    if currentComm is not None:
        if len(args) > 2:
            currentComm(args[2:])


def execute_command(*args):
    global localCommDic
    _command_name = args[0]
    if _command_name in localCommDic.keys():
        localCommDic[_command_name](*args[1:])
    else:
        print("invalid command change")

def load():
    global charDic
    if exists('saveFiles/gamesave.json'):
        print("Savefile exists")
        imported_dic = json.load(open('saveFiles/gamesave.json'))
        for char_name, char_data in imported_dic.items():
            charDic[char_name] = char_from_data(char_data)



def save():
    if not exists('saveFiles/gamesave.json'):
        if not exists('saveFiles'):
            os.mkdir("saveFiles")
        print("created savefile")
    with open('saveFiles/gamesave.json', 'w') as newfile:
        output = {}
        for char in charDic.values():
            temp = toJSON(char)
            output[temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)


charDic = {}
localCommDic = {
    'addC': add_char,
    'cause': cause_damage,
    'take': take_damage,
    'inc' : increase_health,
    'heal': heal,
    'healm': heal_max,
    'log': log
}

currentComm = None
comm_name = None


load()
print("---setup-complete---")
while True:
    print("current characters:")
    names = ''
    for name, char in charDic.items():
        names += ' ' + name
    print(names)
    #if comm_name:
    #    print("current command:", comm_name)
    #else:
        #print("no command chosen")
    print("input command: log, addC, cause, take, heal, healm")
    passed_args = input().split(' ')
    print()
    execute_command(*passed_args)
    save()
    print()
    print("-----------------------------")
    #if passed_args[0] == 'c':
    #    print("changing command")
    #    change_command(*passed_args[1:])
    #if currentComm:
    #currentComm(*passed_args)
    #else:
    #    print("no command assigned yet")
