from .Character import Character
from .campaign_helper import *
from src.command_helper_functions import check_min_command_arg_len

from .packg_variables import localCommDic, charDic
import src.ext.Campaign.Undo as Undo


def log(*args) -> str:
    adv = args[0]
    ret_string = ""
    ptr = Undo.get_pointer()
    if len(charDic.values()) == 0:
        ret_string += "There are no characters at the moment\n"
    for char in charDic.values():
        ret_string += str(char) + "\n"

    if adv:
        ret_string += "---------\n"
        for indx, action in enumerate(Undo.actionQueue):
            if indx == ptr:
                ret_string += "-->"
            ret_string += str(action) + "\n---------\n"

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
    check_char_name(args[0], raise_error=True)

    _char_name = args[0]
    _dam = int(args[1])
    _kills = int(args[2])
    undo_action = Undo.MultipleBaseAction(charDic[_char_name], ["damage_caused", "kills", "max_damage"])
    charDic[_char_name].cause_dam(_dam, _kills)
    undo_action.update(charDic[_char_name])
    Undo.queue_undo_action(undo_action)
    save()
    if _kills > 0:
        return f"character {_char_name} caused {_dam} damage and kills {_kills} enemies"
    return f"character {_char_name} caused {_dam} damage"


# adds Damage taken to a character
# command usage: take char_name damage
def take_damage(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name(args[0], raise_error=True)

    _char_name = args[0]
    _dam = int(args[1])
    _resisted = bool(args[2])
    undo_action = Undo.MultipleBaseAction(charDic[_char_name], ["damage_taken", "health", "faints"])
    fainted, _dam = charDic[_char_name].take_dam(_dam, _resisted)
    undo_action.update(charDic[_char_name])
    Undo.queue_undo_action(undo_action)
    save()
    if fainted:
        return f"character {_char_name} takes {_dam} damage and faints"
    else:
        return f"character {_char_name} takes {_dam} damage"


# heals character to their health maximum, corresponds to a long rest in D&D
# command usage: healm char_name
def heal_max(*args) -> str:
    check_min_command_arg_len(1, *args)
    _char_name = args[0]
    if _char_name == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_max()
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        save()
        print(charDic)
        print(charDic["a"])
        return "all characters were healed"
    check_char_name(_char_name, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[_char_name], ["health", "damage_healed"])
    charDic[_char_name].heal_max()
    undo_action.update(charDic[_char_name])
    Undo.queue_undo_action(undo_action)
    save()
    return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
# command usage: heal char_name amount
def heal(*args) -> str:
    check_min_command_arg_len(2, *args)
    _char_name = args[0]
    _healed = int(args[1])
    if _char_name == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_dam(_healed)
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        save()
        return f"All characters were healed by {_healed}"
    check_char_name(_char_name, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[_char_name], ["health", "damage_healed"])
    charDic[_char_name].heal_dam(_healed)
    undo_action.update(charDic[_char_name])
    Undo.queue_undo_action(undo_action)
    save()
    return "character " + _char_name + " healed " + str(_healed)


# command usage: set_max char_name amount
def set_max_health(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_name(args[0], raise_error=True)
    _char_name = args[0]
    _health_inc = int(args[1])
    undo_action = Undo.MultipleBaseAction(charDic[_char_name], ["health", "max_health"])
    charDic[_char_name].set_max_health(_health_inc)
    undo_action.update(charDic[_char_name])
    Undo.queue_undo_action(undo_action)
    save()
    return "character " + _char_name + " health increased to " + str(_health_inc)


def setup_commands():
    def add_to_commands(com_name: str, command):
        localCommDic[com_name] = command

    # all used commands need to be added in order to work
    add_to_commands('addC', add_char)
    add_to_commands('cause', cause_damage)
    add_to_commands('take', take_damage)
    add_to_commands('set_health', set_max_health)
    add_to_commands('heal', heal)
    add_to_commands('healm', heal_max)
    add_to_commands('log', log)
