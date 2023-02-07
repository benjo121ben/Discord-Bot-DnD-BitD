import decohints
from functools import wraps

from .Character import Character
from .SaveDataManagement.save_file_management import session_tag, character_tag, check_savefile_existence
from .SaveDataManagement.live_save_manager import save_user_file, check_file_loaded, get_loaded_dict, \
    get_loaded_chars, check_file_admin, access_file_as_user, new_save, get_loaded_filename
from .SaveDataManagement.char_data_access import check_char_tag, get_char_tag_by_id, retag_char, check_if_user_has_char
from .campaign_exceptions import CommandException
from . import Undo, UndoActions


@decohints.decohints
def check_and_save_file_wrapper(function_to_wrap):
    """
    Decorator for all functions that require a savefile to be open when used and save the changes after being correctly
    executed

    :param function_to_wrap: the function that is called
    :return: wrapped function
    """
    @wraps(function_to_wrap)
    def wrapped_func(*args, **kwargs):
        user_id = args[0]
        check_file_loaded(user_id, raise_error=True)
        value = function_to_wrap(*args, **kwargs)
        save_user_file(user_id)
        return value
    return wrapped_func


def load_or_create_save(executing_user: str, file_name: str) -> str:
    old_file_name = get_loaded_filename(executing_user)
    if old_file_name is None:
        old_file_name = ""
    ret_str = ""
    if check_file_loaded(file_name) or check_savefile_existence(file_name):
        ret_str = access_file_as_user(executing_user, file_name)
    else:
        ret_str = new_save(executing_user, file_name)
    Undo.queue_undo_action(executing_user, UndoActions.FileChangeUndoAction(old_file_name, file_name))
    return ret_str


def log(executing_user: str, adv=False) -> str:
    ptr = Undo.get_pointer(executing_user)
    save_dic = get_loaded_dict(executing_user)
    char_dic = save_dic[character_tag]
    ret_string = f"**Session {save_dic[session_tag]}**\n"
    if len(char_dic) == 0:
        ret_string += "There are no characters at the moment\n"
    for char in char_dic.values():
        ret_string += str(char) + "\n"

    if adv:
        ret_string += "---------\n"
        for indx, action in enumerate(Undo.get_action_queue(executing_user)):
            if indx == ptr:
                ret_string += "-->"
            ret_string += str(action) + "\n---------\n"

    return ret_string


@check_and_save_file_wrapper
def claim_character(executing_user: str, char_tag: str, assigned_user_id: str):
    check_char_tag(executing_user, char_tag, raise_error=True)
    if check_if_user_has_char(executing_user, assigned_user_id):
        raise CommandException(
            f"this user already has character {get_char_tag_by_id(executing_user, assigned_user_id)} assigned")
    current_player = get_loaded_chars(executing_user)[char_tag].player

    if current_player != "" and int(current_player) != executing_user and not check_file_admin(executing_user):
        raise CommandException(
            "You are not authorized to assign this character. It has already been claimed by a user.")
    get_loaded_chars(executing_user)[char_tag].set_player(assigned_user_id)
    Undo.queue_basic_action(executing_user, char_tag, "player", current_player, str(assigned_user_id))
    return f"character {char_tag} assigned to {assigned_user_id}"


@check_and_save_file_wrapper
def unclaim_char(executing_user: str, char_tag: str):
    _char_dict = get_loaded_chars(executing_user)
    if not check_char_tag(executing_user, char_tag):
        raise CommandException("This character does not exist")
    if _char_dict[char_tag].player == "":
        raise CommandException("This Character was never claimed")
    if _char_dict[char_tag].player != executing_user and not check_file_admin(executing_user):
        raise CommandException("Only file creators can use this command on other people's characters")

    Undo.queue_basic_action(executing_user, char_tag, "player", str(_char_dict[char_tag].player), "")
    get_loaded_chars(executing_user)[char_tag].set_player("")
    return f"Character {char_tag} unassigned"


# adds new character to the roster
@check_and_save_file_wrapper
def add_char(executing_user: str, tag: str, char_name: str, max_health: int) -> str:
    if tag == "all":
        raise CommandException(
            "You are not allowed to call your character all, due to special commands using it as a keyword." +
            " Please call them something else"
        )

    if tag in get_loaded_chars(executing_user):
        return "a character with this tag already exists"
    get_loaded_chars(executing_user)[tag] = Character(tag, char_name, max_health)
    return "character " + char_name + " added"


@check_and_save_file_wrapper
def retag_character(executing_user: str, char_tag_old: str, char_tag_new: str) -> str:
    check_char_tag(executing_user, char_tag_old, raise_error=True)
    if check_char_tag(executing_user, char_tag_new):
        raise CommandException("A Character of this name already exists")
    retag_char(executing_user, char_tag_old, char_tag_new)
    Undo.queue_undo_action(executing_user, UndoActions.RetagCharUndoAction(char_tag_old, char_tag_new))
    return f"Character {char_tag_old} has been renamed to {char_tag_new}"


# increases the caused damage stat
@check_and_save_file_wrapper
def cause_damage(executing_user: str, char_tag: str, dam: int, kills: int) -> str:
    check_char_tag(executing_user, char_tag, raise_error=True)
    dam = abs(dam)
    kills = abs(kills)
    _char_dic = get_loaded_chars(executing_user)
    _char_name = _char_dic[char_tag].name
    undo_action = UndoActions.MultipleBaseAction(_char_dic[char_tag], ["damage_caused", "kills", "max_damage"])
    _char_dic[char_tag].cause_dam(dam, kills)
    undo_action.update(_char_dic[char_tag])
    Undo.queue_undo_action(executing_user, undo_action)
    if kills > 0:
        return f"character {_char_name} caused {dam} damage and kills {kills} enemies"
    return f"character {_char_name} caused {dam} damage"


# adds Damage taken to a character
@check_and_save_file_wrapper
def take_damage(executing_user: str, char_tag: str, dam: int, resisted: bool) -> str:
    check_char_tag(executing_user, char_tag, raise_error=True)
    dam = abs(dam)
    _char_dic = get_loaded_chars(executing_user)
    _char_name = _char_dic[char_tag].name
    undo_action = UndoActions.MultipleBaseAction(_char_dic[char_tag], ["damage_taken", "health", "faints"])
    fainted, dam = _char_dic[char_tag].take_dam(dam, resisted)
    undo_action.update(_char_dic[char_tag])
    Undo.queue_undo_action(executing_user, undo_action)
    if fainted:
        return f"character {_char_name} takes {dam} damage and faints"
    else:
        return f"character {_char_name} takes {dam} damage"


# character damage_taken increased without decreasing health
@check_and_save_file_wrapper
def tank_damage(executing_user: str, char_tag: str, amount: int) -> str:
    check_char_tag(executing_user, char_tag, raise_error=True)
    amount = abs(amount)
    _char_dic = get_loaded_chars(executing_user)
    undo_action = UndoActions.MultipleBaseAction(_char_dic[char_tag], ["damage_taken"])
    _char_dic[char_tag].tank(amount)
    undo_action.update(_char_dic[char_tag])
    Undo.queue_undo_action(executing_user, undo_action)
    return f"{char_tag} tanks {amount} damage"


# heals character to their health maximum, corresponds to a long rest in D&D
@check_and_save_file_wrapper
def heal_max(executing_user: str, char_tag: str) -> str:
    _char_dic = get_loaded_chars(executing_user)
    if char_tag == "all":
        for char in _char_dic.values():
            undo_action = UndoActions.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_max()
            undo_action.update(char)
            Undo.queue_undo_action(executing_user, undo_action)
        return "all characters were healed"
    _char_name = _char_dic[char_tag].name
    check_char_tag(executing_user, char_tag, raise_error=True)
    undo_action = UndoActions.MultipleBaseAction(_char_dic[char_tag], ["health", "damage_healed"])
    _char_dic[char_tag].heal_max()
    undo_action.update(_char_dic[char_tag])
    Undo.queue_undo_action(executing_user, undo_action)
    return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
@check_and_save_file_wrapper
def heal(executing_user: str, char_tag: str, healed: int) -> str:
    healed = abs(healed)
    _char_dic = get_loaded_chars(executing_user)
    if char_tag == "all":
        for char in _char_dic.values():
            undo_action = UndoActions.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_dam(healed)
            undo_action.update(char)
            Undo.queue_undo_action(executing_user, undo_action)
        return f"All characters were healed by {healed}"
    else:
        check_char_tag(executing_user, char_tag, raise_error=True)
        undo_action = UndoActions.MultipleBaseAction(_char_dic[char_tag], ["health", "damage_healed"])
        _char_dic[char_tag].heal_dam(healed)
        undo_action.update(_char_dic[char_tag])
        Undo.queue_undo_action(executing_user, undo_action)
        _char_name = _char_dic[char_tag].name
        return "character " + _char_name + " healed " + str(healed)


# command usage: set_max char_name amount
@check_and_save_file_wrapper
def set_max_health(executing_user: str, char_tag: str, new_max: int) -> str:
    new_max = abs(new_max)
    check_char_tag(executing_user, char_tag, raise_error=True)
    _char_dic = get_loaded_chars(executing_user)
    undo_action = UndoActions.MultipleBaseAction(_char_dic[char_tag], ["health", "max_health"])
    _char_dic[char_tag].set_max_health(new_max)
    undo_action.update(_char_dic[char_tag])
    Undo.queue_undo_action(executing_user, undo_action)
    _char_name = _char_dic[char_tag].name
    return "character " + _char_name + " health increased to " + str(new_max)


@check_and_save_file_wrapper
def crit(executing_user: str, char_tag: str) -> str:
    check_char_tag(executing_user, char_tag, raise_error=True)
    _char_dic = get_loaded_chars(executing_user)
    crits = _char_dic[char_tag].crits
    Undo.queue_basic_action(executing_user, char_tag, "crits", crits, crits + 1)
    _char_dic[char_tag].rolled_crit()
    return f"Crit of {char_tag} increased by 1"


@check_and_save_file_wrapper
def dodge(executing_user: str, char_tag: str) -> str:
    check_char_tag(executing_user, char_tag, raise_error=True)
    _char_dic = get_loaded_chars(executing_user)
    _dodged = _char_dic[char_tag].dodged
    Undo.queue_basic_action(executing_user, char_tag, "dodged", _dodged, _dodged + 1)
    _char_dic[char_tag].dodge()
    return f"Character {char_tag}, dodged an attack"


@check_and_save_file_wrapper
def session_increase(executing_user: str):
    _file_dic = get_loaded_dict(executing_user)
    _file_dic[session_tag] += 1
    return "finished session, increased by one"


def undo_command(executing_user: str, amount: int):
    if amount > 10:
        amount = 10
    ret_val = ""
    for _ in range(amount):
        ret_val += Undo.undo(executing_user) + "\n"
        if not get_loaded_filename(executing_user) == "":
            save_user_file(executing_user)
    return ret_val


def redo_command(executing_user: str, amount: int) -> str:
    ret_val = ""
    for _ in range(amount):
        ret_val += Undo.redo(executing_user) + "\n"
        if not get_loaded_filename(executing_user) == "":
            save_user_file(executing_user)
    return ret_val


# def setup_commands():
#     def add_to_commands(com_name: str, command):
#         localCommDic[com_name] = command
#
#     # all used commands need to be added in order to work
#     add_to_commands('addC', add_char)
#     add_to_commands('cause', cause_damage)
#     add_to_commands('take', take_damage)
#     add_to_commands('set_health', set_max_health)
#     add_to_commands('heal', heal)
#     add_to_commands('healm', heal_max)
#     add_to_commands('log', log)
