import decohints
from functools import wraps

from .Character import Character
from .SaveDataManagement.save_file_management import session_tag, character_tag, check_savefile_existence
from .SaveDataManagement.live_save_manager import save_user_file, check_file_loaded, get_loaded_dict, \
    get_loaded_chars, check_file_admin, access_file_as_user, new_save, get_loaded_filename
from .SaveDataManagement.char_data_access import check_char_tag, get_char_tag_by_id, check_if_user_has_char, get_char
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
    if check_if_user_has_char(executing_user, assigned_user_id):
        raise CommandException(
            f"this user already has character {get_char_tag_by_id(executing_user, assigned_user_id)} assigned")
    _character = get_char(executing_user, char_tag)
    _current_player = _character.player

    if _current_player != "" and _current_player != executing_user and not check_file_admin(executing_user):
        raise CommandException(
            "You are not authorized to assign this character. It has already been claimed by a user.")
    _character.set_player(assigned_user_id)
    Undo.queue_basic_action(executing_user, char_tag, "player", _current_player, assigned_user_id)
    return f"character {char_tag} assigned to {assigned_user_id}"


@check_and_save_file_wrapper
def unclaim_char(executing_user: str, char_tag: str):
    _char = get_char(executing_user, char_tag)
    if _char.player == "":
        raise CommandException("This Character was never claimed")
    if _char.player != executing_user and not check_file_admin(executing_user):
        raise CommandException("Only file creators can use this command on other people's characters")

    Undo.queue_basic_action(executing_user, char_tag, "player", _char.player, "")
    get_loaded_chars(executing_user)[char_tag].set_player("")
    return f"Character {char_tag} unassigned"


# adds new character to the roster
@check_and_save_file_wrapper
def add_char(executing_user: str, tag: str, char_name: str) -> str:
    if tag == "all":
        raise CommandException(
            "You are not allowed to call your character all, due to special commands using it as a keyword." +
            " Please call them something else"
        )

    if check_char_tag(executing_user, tag):
        return "a character with this tag already exists"
    get_loaded_chars(executing_user)[tag] = Character(tag, char_name)
    return "character " + char_name + " added"


@check_and_save_file_wrapper
def retag_character(executing_user: str, char_tag_old: str, char_tag_new: str) -> str:
    check_char_tag(executing_user, char_tag_old, raise_error=True)
    if check_char_tag(executing_user, char_tag_new):
        raise CommandException("A Character of this name already exists")

    _chardict = get_loaded_chars(executing_user)
    _chardict[char_tag_new] = _chardict[char_tag_old]
    _chardict[char_tag_new].tag = char_tag_new
    del _chardict[char_tag_old]

    Undo.queue_undo_action(executing_user, UndoActions.RetagCharUndoAction(char_tag_old, char_tag_new))
    return f"Character {char_tag_old} has been renamed to {char_tag_new}"


# increases the caused damage stat
@check_and_save_file_wrapper
def cause_damage(executing_user: str, char_tag: str, dam: int, kills: int) -> str:
    dam = abs(dam)
    kills = abs(kills)
    _char = get_char(executing_user, char_tag)
    _char_name = _char.name
    undo_action = UndoActions.MultipleBaseAction(_char, ["damage_caused", "kills"])
    _char.cause_dam(dam, kills)
    undo_action.update()
    Undo.queue_undo_action(executing_user, undo_action)
    if kills > 0:
        return f"character {_char_name} caused {dam} damage and kills {kills} enemies"
    return f"character {_char_name} caused {dam} damage"


# adds Damage taken to a character
@check_and_save_file_wrapper
def take_damage(executing_user: str, char_tag: str, dam: int, resisted: bool) -> str:
    dam = abs(dam)
    _char: Character = get_char(executing_user, char_tag)
    _char_name = _char.name
    undo_action = UndoActions.MultipleBaseAction(_char, ["damage_taken", "damage_resisted"])
    dam = _char.take_dam(dam, resisted)
    undo_action.update()
    Undo.queue_undo_action(executing_user, undo_action)
    return f"character {_char_name} takes {dam} damage"


# heals by a certain amount
@check_and_save_file_wrapper
def heal(executing_user: str, char_tag: str, healed: int) -> str:
    healed = abs(healed)
    _char = get_char(executing_user, char_tag)
    undo_action = UndoActions.MultipleBaseAction(_char, ["health", "damage_healed"])
    _char.heal(healed)
    undo_action.update()
    Undo.queue_undo_action(executing_user, undo_action)
    return f"character {_char.name} healed {healed}"


@check_and_save_file_wrapper
def crit(executing_user: str, char_tag: str) -> str:
    _char = get_char(executing_user, char_tag)
    crits = _char.crits
    Undo.queue_basic_action(executing_user, char_tag, "crits", crits, crits + 1)
    _char.rolled_crit()
    return f"Crit of {char_tag} increased by 1"


@check_and_save_file_wrapper
def dodge(executing_user: str, char_tag: str) -> str:
    _char = get_char(executing_user, char_tag)
    _dodged = _char.dodged
    Undo.queue_basic_action(executing_user, char_tag, "dodged", _dodged, _dodged + 1)
    _char.dodge()
    return f"Character {char_tag}, dodged an attack"


@check_and_save_file_wrapper
def session_increase(executing_user: str):
    get_loaded_dict(executing_user)[session_tag] += 1
    return "finished session, increased by one"


def undo_command(executing_user: str, amount: int):
    if amount > 10:
        amount = 10
    ret_val = ""
    for _ in range(amount):
        ret_val += f'{Undo.undo(executing_user)}\n'
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
