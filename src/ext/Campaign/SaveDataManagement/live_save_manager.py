import logging
import threading

from .TempEntryDict import TempEntryDict
from ..campaign_exceptions import NotFileAdminException, NoAssignedSaveException, UserNotPlayerException
from .save_file_management import parse_savefile_contents, save_data_to_file, players_tag, character_tag, \
    get_fresh_save, setup_save_folders, admin_tag

USER_ID_DELETION_TIME = 120
FILE_DELETION_TIME = 60

new_ID_dict = TempEntryDict(USER_ID_DELETION_TIME, "ID")
new_file_dict = TempEntryDict(FILE_DELETION_TIME, "File")
logger = logging.getLogger('bot')


def setup_live_save_data():
    global new_ID_dict, new_file_dict
    setup_save_folders()
    new_ID_dict.clear()
    new_file_dict.clear()


def check_file_loaded(user_id: str, raise_error: bool = False):
    """
    Checks if a save file is currently assigned to a user
    :param user_id: the id of the user trying to access the file
    :param raise_error: If true, the function will throw a NoSaveFileException if there is no currently selected file
    :return: True if character was found, False otherwise
    """
    if get_loaded_filename(user_id) is not None:
        return True
    elif raise_error:
        raise NoAssignedSaveException()
    else:
        return False


def get_loaded_filename(user_id: str):
    global new_ID_dict
    """
    Gets the filename assigned to a user
    :param user_id: the id of the user trying to access their savefile
    :return: The filename assigned to the user or None if no file was assigned
    """
    return new_ID_dict.get(user_id)


def get_loaded_dict(user_id: str):
    global new_ID_dict, new_file_dict
    """
    Gets the savefile dictionary assigned to a user, or None if the user does not have an assigned savefile. If the
    file is not in memory, it will attempt to load the file from the drive, which may cause a SaveFileNotFoundException.
    If a user is not authorized to access the file, this will raise a
    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException
    :raises SaveFileNotFoundException
    :raises NoAssignedSaveException
    """
    _save_name = new_ID_dict.get(user_id)
    if _save_name is None:
        raise NoAssignedSaveException()

    try:
        access_file_as_user(user_id, _save_name)
    except UserNotPlayerException:
        new_ID_dict.remove(user_id)
        raise UserNotPlayerException("It seems you had your access rights to this savefile removed.\n"
                                     "Please contact the admin of the savefile you are trying to access")

    return new_file_dict.get(_save_name)


def check_file_player(user_id: str, _save_name: str, raise_error=False) -> bool:
    global new_file_dict
    load_file_into_memory(_save_name)
    if user_id in new_file_dict.get(_save_name)[players_tag]:
        return True
    elif raise_error:
        raise UserNotPlayerException()
    else:
        return False


def check_file_admin(user_id: str, raise_error=False) -> bool:
    user_dic = get_loaded_dict(user_id)
    if user_dic[admin_tag] == "" or user_id == user_dic[admin_tag]:
        return True
    elif raise_error:
        raise NotFileAdminException()
    else:
        return False


def get_loaded_chars(user_id: str):
    """
    Gets the character dictionary assigned to a user's save, or None if the user does not have an assigned savefile.\n
    If the file is not in memory, it will attempt to load the file from the drive.

    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException: If the user is not authorized to access the file
    :raises SaveFileNotFoundException: If the savefile is not in memory and was deleted from the hardware
    """
    return get_loaded_dict(user_id)[character_tag]


def access_file_as_user(user_id: str, _save_name: str):
    global new_ID_dict
    check_file_player(user_id, _save_name, True)
    new_ID_dict.set(user_id, _save_name)
    return f"Savefile exists.\nLoaded {_save_name} into memory."


def save_user_file(user_id: str):
    file_name = get_loaded_filename(user_id)
    save_data_to_file(file_name, new_file_dict.get(file_name))


def load_file_into_memory(_file_name, replace=False):
    global new_file_dict

    if _file_name not in new_file_dict or replace:
        logger.info(f"{_file_name} WAS LOADED INTO MEMORY")
        new_file_dict.set(_file_name, parse_savefile_contents(_file_name))
        logger.info(f"{_file_name} WAS LOADED INTO MEMORY")


def unload_all_files_and_users():
    global new_file_dict, new_ID_dict
    new_file_dict.clear()
    new_ID_dict.clear()


def new_save(executing_user: str, file_name: str):
    global new_file_dict, new_ID_dict
    logger.info("new save called")
    new_file_dict.set(file_name, get_fresh_save(executing_user))

    new_ID_dict.set(executing_user, file_name)
    return f"savefile name\n**{file_name}**\nhas not been claimed.\n" \
           "Create a character with the add_char command to claim it for yourself, make sure to write down the file's name"


