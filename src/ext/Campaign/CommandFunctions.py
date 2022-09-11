from .Character import Character
from .HelperFunctions import *
from .packg_variables import localCommDic, charDic

save_file_name = ""


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
    if check_min_command_arg_len(3, *args):
        _player_name, _char_name, _max_health = args
        _max_health = int(args[2])
        charDic[_char_name] = Character(_player_name, _char_name,_max_health)
        save()
        return "character " + _char_name + " added"


# command usage: cause char_name damage
def cause_damage(*args) -> str:
    if check_min_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].cause_dam(_dam)
        save()
        return "character " + _char_name + " caused " + str(_dam) + " damage"


# adds Damage taken to a character
# command usage: take char_name damage
def take_damage(*args) -> str:
    if check_min_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].take_dam(_dam)
        save()
        return "character " + _char_name + " takes " + str(_dam) + " damage"


# adds Damage taken to a character
# command usage: take char_name damage
def take_damage_res(*args) -> str:
    if check_min_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _dam = int(args[1])
        charDic[_char_name].take_dam_res(_dam)
        save()
        return "character " + _char_name + " takes " + str(_dam/2) + " damage"


# heals character to their health maximum, corresponds to a long rest in D&D
# command usage: healm char_name
def heal_max(*args) -> str:
    if check_min_command_arg_len(1, *args):
        _char_name = args[0]
        if _char_name == "all":
            for char in charDic.values():
                char.heal_max()
            save()
            return "all characters were healed"
        elif check_char_name(args[0]):
            charDic[_char_name].heal_max()
            save()
            return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
# command usage: heal char_name amount
def heal(*args) -> str:
    if check_min_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _healed = int(args[1])
        charDic[_char_name].heal_dam(_healed)
        save()
        return "character " + _char_name + " healed " + str(_healed)


# command usage: inc char_name amount
def increase_health(*args) -> str:
    if check_min_command_arg_len(2, *args) and check_char_name(args[0]):
        _char_name = args[0]
        _health_inc = int(args[1])
        charDic[_char_name].inc_max_health(_health_inc)
        save()
        return "character " + _char_name + " health increased by " + str(_health_inc)


def setup_commands():
    def add_to_commands(com_name: str, command):
        localCommDic[com_name] = command

    get_save_file() #make user insert a savefile

    # all used commands need to be added in order to work
    add_to_commands('addC', add_char)
    add_to_commands('cause', cause_damage)
    add_to_commands('take', take_damage)
    add_to_commands('inc', increase_health)
    add_to_commands('heal', heal)
    add_to_commands('healm', heal_max)
    add_to_commands('log', log)
