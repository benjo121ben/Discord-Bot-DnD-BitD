import logging

from discord.ext.bridge import BridgeExtContext

from .campaign_exceptions import NotFileAdminException
from ..command_exceptions import CommandException
from .save_file_management import load_file, save_data_to_file, players_tag, character_tag, last_changed_tag, \
    get_fresh_save

ID_dic = {}
file_dic = {}
logger = logging.getLogger('bot')


class NoAssignedSaveException(CommandException):
    def __init__(self, m=""):
        if m == "":
            m = "No savefile has been loaded. Use the load command to load an existing file or create a new one"
        super(m)


class UserNotPlayerException(CommandException):
    def __init__(self, m=""):
        if m == "":
            m = "You are not a participant in this game, the admin of the file needs to add you via the add_player " \
                "command"
        super(m)


def get_user_save_name(user_id: str):
    """
    Gets the filename assigned to a user
    :param user_id: the id of the user trying to access their savefile
    :return: The filename assigned to the user or None if no file was assigned
    """
    if user_id in ID_dic:
        return ID_dic[user_id]
    else:
        return None


def get_user_save_dic(user_id: str):
    """
    Gets the savefile dictionary assigned to a user, or None if the user does not have an assigned savefile. If the
    file is not in memory, it will attempt to load the file from the drive, which may cause a SaveFileNotFoundException.
    If a user is not authorized to access the file, this will raise a
    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException
    :raises SaveFileNotFoundException
    """
    _save_name = get_user_save_name(user_id)
    if _save_name is None:
        return None

    if _save_name not in file_dic:
        try:
            load(user_id, _save_name)
        except UserNotPlayerException:
            raise UserNotPlayerException("It seems you had your access rights to this savefile removed.\n"
                                         "Please contact the admin of the savefile you are trying to access")
    return file_dic[_save_name]


def get_user_char_dic(user_id: str):
    """
    Gets the character dictionary assigned to a user's save, or None if the user does not have an assigned savefile.\n
    If the file is not in memory, it will attempt to load the file from the drive.

    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException: If the user is not authorized to access the file
    :raises SaveFileNotFoundException: If the savefile is not in memory and was deleted from the hardware
    """
    _save_name = get_user_save_name(user_id)
    if _save_name is None:
        return None

    if _save_name not in file_dic:
        try:
            load(user_id, _save_name)
        except UserNotPlayerException:
            raise UserNotPlayerException("It seems you had your access rights to this savefile removed.\n"
                                         "Please contact the admin of the savefile you are trying to access")
    return file_dic[_save_name][character_tag]


def check_file_loaded(user_id: str, raise_error: bool = False):
    """
    Checks if a save file is currently assigned to a user
    :param user_id: the id of the user trying to access the file
    :param raise_error: If true, the function will throw a NoSaveFileException if there is no currently selected file
    :return: True if character was found, False otherwise
    """
    if get_user_save_name(user_id) is not None:
        return True
    elif raise_error:
        raise NoAssignedSaveException()
    else:
        return False


def load(user_id: str, _save_name):
    if _save_name not in file_dic:
        file_dic[_save_name] = load_file(_save_name)

    ID_dic[user_id] = _save_name
    return f"Savefile exists.\nLoaded {_save_name} into memory."


def new_save(executing_user: str, file_name: str):
    logger.info("new save called")
    file_dic[file_name] = get_fresh_save()
    ID_dic[executing_user] = file_name
    return f"savefile name\n**{file_name}**\nhas not been claimed.\n" \
           "Create a character with the add_char command to claim it for yourself, make sure to write down the file's name"


def save_user_file(user_id: str):
    _save_name = get_user_save_name(user_id)
    save_by_filename(_save_name)


def save_by_filename(_save_name: str):
    if _save_name not in file_dic:
        raise Exception(f"trying to save a file that is not in memory: {_save_name}")
    save_data_to_file(_save_name, file_dic[_save_name])
    logger.info(f"time in memory {file_dic[_save_name][last_changed_tag]}")


def set_user_save(user_id: str, _save_name: str):
    ID_dic[user_id] = _save_name


def clear_user_save(user_id: str):
    del ID_dic[user_id]


def check_if_user_has_char(executing_user: str, search_user_id: str) -> bool:
    for char in get_user_char_dic(executing_user):
        if char.player == search_user_id:
            return True
    return False


def get_char_tag_by_id(executing_user: str, search_user_id: str):
    if not check_if_user_has_char(executing_user, search_user_id):
        raise CommandException("get_tag_by_id: attempted to get the character of an unassigned user")
    for char in get_user_char_dic(search_user_id):
        if char.player == search_user_id:
            return char.tag


def get_char_name_by_id(executing_user: str, search_user_id: str):
    if not check_if_user_has_char(executing_user, search_user_id):
        raise CommandException("get_char_name_by_id: attempted to get the character of an unassigned user")
    for char in get_user_char_dic(executing_user):
        if char.player == str(search_user_id):
            return char.name


def check_char_tag(executing_user: str, char_tag: str, raise_error: bool = False):
    """
    Checks if a character with this tag exists in the current save file
    :param executing_user: id of executing user
    :param char_tag: tag of checked character
    :param raise_error: If true, the function will throw a CommandException if the character was not found
    :return: True if character was found, False otherwise
    """
    if not check_file_loaded(executing_user, raise_error=raise_error):
        return False
    if char_tag is None:
        if raise_error:
            raise CommandException(
                "campaign_helper:check_char_tag: Character tag None was given. "
                "This should never happen, please contact the developer."
            )
    elif char_tag in get_user_char_dic(executing_user):
        return True
    elif raise_error:
        raise CommandException("Character doesn't exist")
    return False


def get_char_tag_if_none(ctx: BridgeExtContext, char_tag: str = None):
    if char_tag is not None:
        return char_tag

    user_id = str(ctx.author.id)
    check_file_loaded(user_id, raise_error=True)
    char_dic = get_user_char_dic(user_id)
    for char in char_dic.values():
        if char.player == str(ctx.author.id):
            return char.tag
    raise CommandException(
        "No character is assigned to you. Either claim a character or add the char_tag as a parameter")


def check_file_admin(user_id: str, raise_error=False) -> bool:
    raise NotFileAdminException("check_file_admin Not implemented!!!")
    # if p_vars.bot_admin_id is None or user_id == p_vars.bot_admin_id:
    #     return True
    # elif raise_error:
    #     raise NotFileAdminException()
    # else:
    #     return False


def check_file_player(user_id: int, _save_name: str, raise_error=False) -> bool:
    if user_id in file_dic[_save_name][players_tag]:
        return True
    elif raise_error:
        raise UserNotPlayerException()
    else:
        return False
