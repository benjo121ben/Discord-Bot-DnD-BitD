from .Character import Character
from .campaign_helper import *
from src.command_helper_functions import check_min_command_arg_len

from .packg_variables import localCommDic, charDic, imported_dic
from . import Undo


def log(*args) -> str:
    adv = args[0]
    ptr = Undo.get_pointer()
    check_file_loaded(raise_error=True)
    ret_string = f"**Session {imported_dic['session']}**\n"
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


# adds new character to the roster
# command usage: addC tag char_name max_health
def add_char(*args) -> str:
    check_min_command_arg_len(3, *args)

    _tag = args[0]
    _char_name = args[1]
    if charDic.__contains__(_tag):
        return "a character with this tag already exists"

    _max_health = int(args[2])
    charDic[_tag] = Character(_tag, _char_name, _max_health)
    save()
    return "character " + _char_name + " added"


# command usage: cause char_tag damage
def cause_damage(*args) -> str:
    check_min_command_arg_len(2, *args)
    _char_tag = args[0]
    check_char_tag(_char_tag, raise_error=True)
    _char_name = charDic[_char_tag].name
    _dam = int(args[1])
    _kills = int(args[2])
    undo_action = Undo.MultipleBaseAction(charDic[_char_tag], ["damage_caused", "kills", "max_damage"])
    charDic[_char_tag].cause_dam(_dam, _kills)
    undo_action.update(charDic[_char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    if _kills > 0:
        return f"character {_char_name} caused {_dam} damage and kills {_kills} enemies"
    return f"character {_char_name} caused {_dam} damage"


# adds Damage taken to a character
# command usage: take char_tag damage
def take_damage(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_tag(args[0], raise_error=True)

    _char_tag = args[0]
    _dam = int(args[1])
    _resisted = bool(args[2])
    _char_name = charDic[_char_tag].name
    undo_action = Undo.MultipleBaseAction(charDic[_char_tag], ["damage_taken", "health", "faints"])
    fainted, _dam = charDic[_char_tag].take_dam(_dam, _resisted)
    undo_action.update(charDic[_char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    if fainted:
        return f"character {_char_name} takes {_dam} damage and faints"
    else:
        return f"character {_char_name} takes {_dam} damage"


# heals character to their health maximum, corresponds to a long rest in D&D
# command usage: healm char_tag
def heal_max(*args) -> str:
    check_min_command_arg_len(1, *args)
    _char_tag = args[0]
    if _char_tag == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_max()
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        save()
        return "all characters were healed"
    _char_name = charDic[_char_tag].name
    check_char_tag(_char_tag, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[_char_tag], ["health", "damage_healed"])
    charDic[_char_tag].heal_max()
    undo_action.update(charDic[_char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
# command usage: heal char_tag amount
def heal(*args) -> str:
    check_min_command_arg_len(2, *args)
    _char_tag = args[0]
    _healed = int(args[1])
    if _char_tag == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_dam(_healed)
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        save()
        return f"All characters were healed by {_healed}"
    check_char_tag(_char_tag, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[_char_tag], ["health", "damage_healed"])
    charDic[_char_tag].heal_dam(_healed)
    undo_action.update(charDic[_char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    _char_name = charDic[_char_tag].name
    return "character " + _char_name + " healed " + str(_healed)


# command usage: set_max char_name amount
def set_max_health(*args) -> str:
    check_min_command_arg_len(2, *args)
    check_char_tag(args[0], raise_error=True)
    _char_tag = args[0]
    _health_inc = int(args[1])
    undo_action = Undo.MultipleBaseAction(charDic[_char_tag], ["health", "max_health"])
    charDic[_char_tag].set_max_health(_health_inc)
    undo_action.update(charDic[_char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    _char_name = charDic[_char_tag].name
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
