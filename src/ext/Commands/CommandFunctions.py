from src.Character import Character
from .HelperFunctions import *


def log(*_):
    for char in charDic.values():
        print(char)


# adds new character to the roster, binding them to a player
# command usage: addC player_name char_name max_health
def add_char(*args):
    if check_command_arg_len(3, *args):
        _player_name, _char_name, _max_health = args
        _max_health = int(args[2])
        charDic[_char_name] = Character(_player_name, _char_name,_max_health)
        return "character " + _char_name + " added"


# command usage: cause char_name damage
def cause_damage(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].cause_dam(_dam)
        return "character " +  _char_name, " caused " + str(_dam) + " damage "


# adds Damage taken to a character
# command usage: take char_name damage
def take_damage(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].take_dam(_dam)
        return "character " + _char_name + " takes " + str(_dam) + " damage"


# heals character to their health maximum, corresponds to a long rest in D&D
# command usage: healm char_name
def heal_max(*args):
    if check_command_arg_len(1, *args) and check_char_name(args[0]):
        _char_name = args[0]
        charDic[_char_name].heal_max()
        return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
# command usage: heal char_name amount
def heal(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _healed = int(args[1])
        charDic[_char_name].heal_dam(_healed)
        return "character " + _char_name + " healed " + str(_healed)


# command usage: inc char_name amount
def increase_health(*args):
    if check_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _health_inc = int(args[1])
        charDic[_char_name].inc_max_health(_health_inc)
        return "character " + _char_name + " health increased by " + str(_health_inc)
