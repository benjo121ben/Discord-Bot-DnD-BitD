import decohints
from functools import wraps

from .Character import Character
from .campaign_helper import check_if_user_has_char, get_char_tag_by_id, check_file_admin, check_char_tag
from .save_file_management import session_tag, check_file_loaded, load_user_file, save_user_file, get_user_filename_no_suff
from .campaign_exceptions import CommandException
from .packg_variables import ID_dic, file_dic
from . import Undo


@decohints.decohints
def check_file_save_file_wrapper(function_to_wrap):
    """
    Decorator for all functions that require a savefile to be open when used and save the changes after being correctly executed
    :param function_to_wrap: the function that is called
    :return: wrapped function
    """
    @wraps(function_to_wrap)
    def wrapped_func(*args, **kwargs):
        user_id = kwargs["user_id"]
        check_file_loaded(user_id, raise_error=True)
        value = function_to_wrap(*args, **kwargs)
        save_user_file(user_id)
        return value
    return wrapped_func


def load_file(user_id, file_name: str) -> str:
    old_file_name = get_user_filename_no_suff(user_id)
    ret_str = load_user_file(user_id, file_name)
    Undo.queue_undo_action(Undo.FileChangeUndoAction(old_file_name, file_name))
    return ret_str


def log(user_id: str, adv=False) -> str:
    ptr = Undo.get_pointer()
    check_file_loaded(user_id, raise_error=True)
    ret_string = f"**Session {file_dic[user_id]['session']}**\n"
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


@check_file_save_file_wrapper
def claim_character(executing_user: int, char_tag: str, assigned_user_id: int):
    check_char_tag(char_tag, raise_error=True)
    if check_if_user_has_char(assigned_user_id):
        raise CommandException(
            f"this user already has character {get_char_tag_by_id(assigned_user_id)} assigned")
    current_player = charDic[char_tag].player

    if current_player != "" and int(current_player) != executing_user and not check_file_admin(executing_user):
        raise CommandException(
            "You are not authorized to assign this character. It has already been claimed by a user.")
    charDic[char_tag].set_player(assigned_user_id)
    Undo.queue_basic_action(char_tag, "player", current_player, str(assigned_user_id))
    return f"character {char_tag} assigned to {assigned_user_id}"


@check_file_save_file_wrapper
def unclaim_user(executing_user: int, to_unclaim_user_id: int):
    if to_unclaim_user_id != executing_user and not check_file_admin(executing_user):
        raise CommandException("You are not authorized to use this command on other people's characters")
    if not check_if_user_has_char(to_unclaim_user_id):
        raise CommandException("this user has no character assigned")
    char_tag = get_char_tag_by_id(to_unclaim_user_id)
    Undo.queue_basic_action(char_tag, "player", str(to_unclaim_user_id), "")
    charDic[char_tag].set_player("")
    return f"Character {char_tag} unassigned"


# adds new character to the roster
@check_file_save_file_wrapper
def add_char(tag: str, char_name: str, max_health: int) -> str:
    if tag == "all":
        raise CommandException(
            "You are not allowed to call your character all, due to special commands using it a keyword."
            " Please call them something else"
        )

    if tag in charDic.keys():
        return "a character with this tag already exists"
    charDic[tag] = Character(tag, char_name, max_health)
    return "character " + char_name + " added"


@check_file_save_file_wrapper
def retag_character(char_tag_old: str, char_tag_new: str)->str:
    check_char_tag(char_tag_old, raise_error=True)
    if check_char_tag(char_tag_new):
        raise CommandException("A Character of this name already exists")

    charDic[char_tag_new] = charDic[char_tag_old]
    charDic[char_tag_new].tag = char_tag_new
    del charDic[char_tag_old]
    Undo.queue_undo_action(Undo.ReTagCharUndoAction(char_tag_old, char_tag_new))
    return f"Character {char_tag_old} has been renamed to {char_tag_new}"


# increases the caused damage stat
@check_file_save_file_wrapper
def cause_damage(char_tag: str, dam: int, kills: int) -> str:
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    dam = abs(dam)
    kills = abs(kills)
    _char_name = charDic[char_tag].name
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["damage_caused", "kills", "max_damage"])
    charDic[char_tag].cause_dam(dam, kills)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    if kills > 0:
        return f"character {_char_name} caused {dam} damage and kills {kills} enemies"
    return f"character {_char_name} caused {dam} damage"


# adds Damage taken to a character
@check_file_save_file_wrapper
def take_damage(char_tag: str, dam: int, resisted: bool) -> str:
    check_char_tag(char_tag, raise_error=True)
    dam = abs(dam)
    _char_name = charDic[char_tag].name
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["damage_taken", "health", "faints"])
    fainted, dam = charDic[char_tag].take_dam(dam, resisted)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    if fainted:
        return f"character {_char_name} takes {dam} damage and faints"
    else:
        return f"character {_char_name} takes {dam} damage"


# character damage_taken increased without decreasing health
@check_file_save_file_wrapper
def tank_damage(char_tag: str, amount: int) -> str:
    check_char_tag(char_tag, raise_error=True)
    amount = abs(amount)
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["damage_taken"])
    charDic[char_tag].tank(amount)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    return f"{char_tag} tanks {amount} damage"


# heals character to their health maximum, corresponds to a long rest in D&D
@check_file_save_file_wrapper
def heal_max(char_tag: str) -> str:
    if char_tag == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_max()
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        return "all characters were healed"
    _char_name = charDic[char_tag].name
    check_char_tag(char_tag, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["health", "damage_healed"])
    charDic[char_tag].heal_max()
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
@check_file_save_file_wrapper
def heal(char_tag: str, healed: int) -> str:
    healed = abs(healed)
    if char_tag == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_dam(healed)
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        return f"All characters were healed by {healed}"
    else:
        check_char_tag(char_tag, raise_error=True)
        undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["health", "damage_healed"])
        charDic[char_tag].heal_dam(healed)
        undo_action.update(charDic[char_tag])
        Undo.queue_undo_action(undo_action)
        _char_name = charDic[char_tag].name
        return "character " + _char_name + " healed " + str(healed)


# command usage: set_max char_name amount
@check_file_save_file_wrapper
def set_max_health(char_tag: str, new_max: int) -> str:
    new_max = abs(new_max)
    check_char_tag(char_tag, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["health", "max_health"])
    charDic[char_tag].set_max_health(new_max)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    _char_name = charDic[char_tag].name
    return "character " + _char_name + " health increased to " + str(new_max)


@check_file_save_file_wrapper
def crit(char_tag: str) -> str:
    check_char_tag(char_tag, raise_error=True)
    crits = charDic[char_tag].crits
    Undo.queue_basic_action(char_tag, "crits", crits, crits + 1)
    charDic[char_tag].rolled_crit()
    return f"Crit of {char_tag} increased by 1"


@check_file_save_file_wrapper
def dodged(char_tag:str) -> str:
    check_char_tag(char_tag, raise_error=True)
    dodged = charDic[char_tag].dodged
    Undo.queue_basic_action(char_tag, "dodged", dodged, dodged + 1)
    charDic[char_tag].dodge()
    return f"Character {char_tag}, dodged an attack"


@check_file_save_file_wrapper
def session_increase():
    imported_dic[session_tag] += 1
    return "finished session, increased by one"


def undo_command(amount: int):
    check_file_loaded(raise_error=True)
    if amount > 10:
        amount = 10
    ret_val = ""
    for _ in range(amount):
        ret_val += Undo.undo() + "\n"
        if not get_current_save_file_name_no_suff() == "":
            save()
    return ret_val


def redo_command(amount: int) -> str:
    check_file_loaded(raise_error=True)
    ret_val = ""
    for _ in range(amount):
        ret_val += Undo.redo() + "\n"
        if not get_current_save_file_name_no_suff() == "":
            save()
    return ret_val


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
