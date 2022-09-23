from .Character import Character
from .campaign_helper import *
from src.command_helper_functions import check_min_command_arg_len

from .packg_variables import localCommDic, charDic


def log(*_) -> str:
    ret_string = ""
    if len(charDic.values()) == 0:
        return "There are no characters at the moment"
    for char in charDic.values():
        ret_string += str(char) + "\n"

    return ret_string


# adds new character to the roster, binding them to a player
# command usage: addC player_name char_name max_health
def add_char(*args) -> str:
    check_min_command_arg_len(2, *args)

    _char_name = args[0]
    if charDic.__contains__(_char_name):
        return "a character with this name already exists"

    _max_health = int(args[1])
    charDic[_char_name] = Character("", _char_name, _max_health)
    save()
    return "character " + _char_name + " added"


# command usage: cause char_name damage
def cause_damage(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name_error_raise(args[0])

    _char_name = args[0]
    _dam = int(args[1])
    charDic[_char_name].cause_dam(_dam)
    save()
    return "character " + _char_name + " caused " + str(_dam) + " damage"


# adds Damage taken to a character
# command usage: take char_name damage
def take_damage(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name_error_raise(args[0])

    _char_name = args[0]
    _dam = int(args[1])
    charDic[_char_name].take_dam(_dam)
    save()
    return "character " + _char_name + " takes " + str(_dam) + " damage"


# adds Damage taken to a character
# command usage: take char_name damage
def take_damage_res(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name_error_raise(args[0])

    _char_name = args[0]
    _dam = int(args[1])
    charDic[_char_name].take_dam_res(_dam)
    save()
    return "character " + _char_name + " takes " + str(int(_dam/2)) + " damage"


# heals character to their health maximum, corresponds to a long rest in D&D
# command usage: healm char_name
def heal_max(*args) -> str:
    check_min_command_arg_len(1, *args)
    _char_name = args[0]
    if _char_name == "all":
        for char in charDic.values():
            char.heal_max()
        save()
        return "all characters were healed"
    elif check_char_name_error_raise(args[0]):
        charDic[_char_name].heal_max()
        save()
        return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
# command usage: heal char_name amount
def heal(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name_error_raise(args[0])
    _char_name = args[0]
    _healed = int(args[1])
    charDic[_char_name].heal_dam(_healed)
    save()
    return "character " + _char_name + " healed " + str(_healed)


# command usage: set_max char_name amount
def set_max_health(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name_error_raise(args[0])
    _char_name = args[0]
    _health_inc = int(args[1])
    charDic[_char_name].set_max_health(_health_inc)
    save()
    return "character " + _char_name + " health increased by " + str(_health_inc)


def setup_commands():
    def add_to_commands(com_name: str, command):
        localCommDic[com_name] = command

    # all used commands need to be added in order to work
    add_to_commands('addC', add_char)
    add_to_commands('cause', cause_damage)
    add_to_commands('take', take_damage)
    add_to_commands('takeR', take_damage_res)
    add_to_commands('set_health', set_max_health)
    add_to_commands('heal', heal)
    add_to_commands('healm', heal_max)
    add_to_commands('log', log)
