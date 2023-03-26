import logging

import decohints
from functools import wraps

from discord.ext.bridge import BridgeExtContext
import discord.errors as d_errors
from .Character import Character
from .SaveDataManagement.save_file_management import session_tag, character_tag, version_tag, check_savefile_existence, \
    get_savefile_as_discord_file
from .SaveDataManagement.live_save_manager import save_user_file, check_file_loaded, get_loaded_dict, \
    get_loaded_chars, check_file_admin, access_file_as_user, create_new_save, get_loaded_filename, add_player_to_save, rem_player_from_save
from .SaveDataManagement.char_data_access import check_char_tag, get_char_tag_by_id, check_if_user_has_char, get_char, \
    retag_char
from .campaign_exceptions import CommandException
from .campaign_helper import check_bot_admin, get_bot
from . import Undo, UndoActions, packg_variables as cmp_vars

logger = logging.getLogger('bot')


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


@decohints.decohints
def check_and_save_file_wrapper_async(function_to_wrap):
    """
    Decorator for all functions that require a savefile to be open when used and save the changes after being correctly
    executed

    :param function_to_wrap: the function that is called
    :return: wrapped function
    """
    @wraps(function_to_wrap)
    async def wrapped_func(*args, **kwargs):
        user_id = args[0]
        check_file_loaded(user_id, raise_error=True)
        value = await function_to_wrap(*args, **kwargs)
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
        ret_str = create_new_save(executing_user, file_name)
    Undo.queue_undo_action(executing_user, UndoActions.LoadFileUndoAction(old_file_name, file_name))
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


@check_and_save_file_wrapper_async
async def claim_character(executing_user: str, ctx: BridgeExtContext, char_tag: str, assigned_user_id: str):
    if assigned_user_id is None:
        assigned_user_id = str(ctx.author.id)
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

    user = None
    try:
        bot = get_bot()
        user = await bot.fetch_user(int(assigned_user_id))
    except Exception as err:
        logger.error(err)
        await ctx.respond("An error has occurred while fetching the user with this ID.\n")
        Undo.undo(executing_user)
        Undo.discard_undo_queue_after_pointer(executing_user)
        return
    add_player_to_save(executing_user, assigned_user_id)
    await ctx.respond(f"{char_tag} assigned to {user.name}")


@check_and_save_file_wrapper
def unclaim_char(executing_user: str, char_tag: str):
    _char = get_char(executing_user, char_tag)
    if _char.player == "":
        raise CommandException("This Character was never claimed")
    if _char.player != executing_user and not check_file_admin(executing_user):
        raise CommandException("Only file creators can use this command on other people's characters")
    old_player = _char.player
    get_loaded_chars(executing_user)[char_tag].set_player("")
    Undo.queue_basic_action(executing_user, char_tag, "player", old_player, "")
    return f"Character {char_tag} unassigned"


@check_and_save_file_wrapper
def remove_player(executing_user: str, user_id: str):
    return rem_player_from_save(executing_user, user_id)


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
    if len(get_loaded_chars(executing_user)) == 10:
        return "You already have 10 characters, this is the maximum amount"
    get_loaded_chars(executing_user)[tag] = Character(tag, char_name)
    return "character " + char_name + " added"


@check_and_save_file_wrapper
def retag_character(executing_user: str, char_tag_old: str, char_tag_new: str) -> str:
    retag_char(executing_user, char_tag_old, char_tag_new)
    Undo.queue_undo_action(executing_user, UndoActions.RetagCharUndoAction(char_tag_old, char_tag_new))
    return f"Character tag {char_tag_old} has been changed to {char_tag_new}"


@check_and_save_file_wrapper
def rename_character(executing_user: str, char_tag: str, new_char_name: str) -> str:
    _char = get_char(executing_user, char_tag)
    old_val = _char.name
    _char.name = new_char_name
    Undo.queue_basic_action(executing_user, char_tag, "name", old_val, new_char_name)

    return f"Character {old_val} has been renamed to {new_char_name}"


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
    undo_action = UndoActions.MultipleBaseAction(_char, ["damage_healed"])
    _char.heal(healed)
    undo_action.update()
    Undo.queue_undo_action(executing_user, undo_action)
    return f"character {_char.name} healed {healed}"


@check_and_save_file_wrapper
def crit(executing_user: str, char_tag: str, amount: int = 1) -> str:
    _char = get_char(executing_user, char_tag)
    crits = _char.crits
    _char.rolled_crit(amount)
    Undo.queue_basic_action(executing_user, char_tag, "crits", crits, crits + amount)
    return f"Crit of {char_tag} increased by 1"


@check_and_save_file_wrapper
def faint(executing_user: str, char_tag: str, amount: int = 1) -> str:
    _char = get_char(executing_user, char_tag)
    faints = _char.faints
    _char.faint(amount)
    Undo.queue_basic_action(executing_user, char_tag, "faints", faints, faints + amount)
    return f"{char_tag} went unconcious"


@check_and_save_file_wrapper
def dodge(executing_user: str, char_tag: str, amount: int = 1) -> str:
    _char = get_char(executing_user, char_tag)
    _dodged = _char.dodged
    _char.dodge(amount)
    Undo.queue_basic_action(executing_user, char_tag, "dodged", _dodged, _dodged + amount)
    return f"Character {char_tag}, dodged an attack"


@check_and_save_file_wrapper
def session_increase(executing_user: str):
    check_file_admin(executing_user, raise_error=True)
    current_session = get_loaded_dict(executing_user)[session_tag]
    get_loaded_dict(executing_user)[session_tag] += 1
    Undo.queue_undo_action(executing_user, UndoActions.ChangeFileDataUndoAction(session_tag, current_session, current_session + 1))
    return "finished session, increased by one"


async def cache_file(executing_user: str, ctx: BridgeExtContext):
    """
    Sends the current savefile into the discord chat with the ID assigned in the campaign environment file
    :param ctx: Discord context
    :param executing_user: user_id of executing user
    :raises NoSaveFileException if no savefile is present
    :raises NotBotAdminException if user is not the bots admin
    """
    check_file_loaded(executing_user, raise_error=True)
    check_bot_admin(ctx, raise_error=True)
    check_file_admin(executing_user, raise_error=True)

    chat_id = cmp_vars.cache_folder
    if chat_id is None:
        raise CommandException("No cloudsavechannel id assigned")
    file_name = get_loaded_filename(executing_user)
    save_dic = get_loaded_dict(executing_user)
    message = f"cache-{file_name}-session {save_dic[session_tag]}-{save_dic[version_tag]}"
    current_file = get_savefile_as_discord_file(file_name)
    await get_bot().get_channel(chat_id).send(message, file=current_file)
    await ctx.respond("cached")


def undo_command(executing_user: str, amount: int):
    if amount > 10:
        amount = 10
    ret_val = ""
    for _ in range(amount):
        keep_going, text = Undo.undo(executing_user)
        ret_val += f'{text}\n'
        if get_loaded_filename(executing_user) is not None:
            save_user_file(executing_user)
        if not keep_going:
            return ret_val
    return ret_val


def redo_command(executing_user: str, amount: int) -> str:
    ret_val = ""

    for _ in range(amount):
        keep_going, text = Undo.redo(executing_user)
        ret_val += f'{text}\n'
        if get_loaded_filename(executing_user) is not None:
            save_user_file(executing_user)
        if not keep_going:
            return ret_val
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
