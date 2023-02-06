import logging
import threading

from .TempEntryDict import TempEntryDict
from ..campaign_exceptions import NotFileAdminException, NoAssignedSaveException, UserNotPlayerException
from .save_file_management import parse_savefile_contents, save_data_to_file, players_tag, character_tag, \
    get_fresh_save, setup_save_folders, admin_tag

# labels
TIMER_LABEL = 'timer'
SAVE_LABEL = 'save'
FILENAME_LABEL = 'filename'

USER_ID_DELETION_TIME = 120
FILE_DELETION_TIME = 60

new_ID_dict = TempEntryDict(USER_ID_DELETION_TIME)
new_file_dict = TempEntryDict(FILE_DELETION_TIME)
ID_dict = {}
file_dict = {}
logger = logging.getLogger('bot')


def setup_live_save_data():
    global ID_dict, file_dict
    setup_save_folders()
    ID_dict = {}
    file_dict = {}


def get_ID_deletion_timer(user_id: str):
    return threading.Timer(USER_ID_DELETION_TIME, lambda: clear_user_file_link(user_id))


def get_file_mem_deletion_timer(filename: str):
    return threading.Timer(FILE_DELETION_TIME, lambda: clear_file_dict_entry(filename))


def check_file_loaded(user_id: str, raise_error: bool = False):
    """
    Checks if a save file is currently assigned to a user
    :param user_id: the id of the user trying to access the file
    :param raise_error: If true, the function will throw a NoSaveFileException if there is no currently selected file
    :return: True if character was found, False otherwise
    """
    if get_user_loaded_file_name(user_id) is not None:
        return True
    elif raise_error:
        raise NoAssignedSaveException()
    else:
        return False


def check_file_player(user_id: str, _save_name: str, raise_error=False) -> bool:
    load_file_into_memory(_save_name)
    if user_id in get_file_dict_save(_save_name)[players_tag]:
        return True
    elif raise_error:
        raise UserNotPlayerException()
    else:
        return False


def check_file_admin(user_id: str, raise_error=False) -> bool:
    if get_user_loaded_dict(user_id)[admin_tag] == "" or user_id == get_user_loaded_dict(user_id)[admin_tag]:
        return True
    elif raise_error:
        raise NotFileAdminException()
    else:
        return False


def get_user_loaded_file_name(user_id: str):
    global ID_dict
    """
    Gets the filename assigned to a user
    :param user_id: the id of the user trying to access their savefile
    :return: The filename assigned to the user or None if no file was assigned
    """
    if user_id in ID_dict:
        reset_user_timer(user_id)
        return ID_dict[user_id][FILENAME_LABEL]
    else:
        return None


def get_user_loaded_dict(user_id: str):
    """
    Gets the savefile dictionary assigned to a user, or None if the user does not have an assigned savefile. If the
    file is not in memory, it will attempt to load the file from the drive, which may cause a SaveFileNotFoundException.
    If a user is not authorized to access the file, this will raise a
    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException
    :raises SaveFileNotFoundException
    """
    _save_name = get_user_loaded_file_name(user_id)
    if _save_name is None:
        return None

    try:
        access_file_as_user(user_id, _save_name)
    except UserNotPlayerException:
        clear_user_file_link(user_id)
        raise UserNotPlayerException("It seems you had your access rights to this savefile removed.\n"
                                     "Please contact the admin of the savefile you are trying to access")

    return get_file_dict_save(_save_name)


def get_user_loaded_chars(user_id: str):
    """
    Gets the character dictionary assigned to a user's save, or None if the user does not have an assigned savefile.\n
    If the file is not in memory, it will attempt to load the file from the drive.

    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException: If the user is not authorized to access the file
    :raises SaveFileNotFoundException: If the savefile is not in memory and was deleted from the hardware
    """
    _dict = get_user_loaded_dict(user_id)
    if _dict is None:
        return None
    return _dict[character_tag]


def access_file_as_user(user_id: str, _save_name):
    check_file_player(user_id, _save_name, True)
    set_user_file_link(user_id, _save_name)
    reset_file_timer(_save_name)
    return f"Savefile exists.\nLoaded {_save_name} into memory."


def save_user_file(user_id: str):
    file_name = get_user_loaded_file_name(user_id)
    save_data_to_file(file_name, get_file_dict_save(file_name))


def load_file_into_memory(_file_name, replace=False):
    global file_dict

    if _file_name not in file_dict or replace:
        logger.info(f"{_file_name} WAS LOADED INTO MEMORY")
        insert_into_file_dict(_file_name, parse_savefile_contents(_file_name))
        logger.info(f"{_file_name} WAS LOADED INTO MEMORY")
    reset_file_timer(_file_name)


def new_save(executing_user: str, file_name: str):
    logger.info("new save called")
    insert_into_file_dict(file_name, get_fresh_save(executing_user))

    set_user_file_link(executing_user, file_name)
    return f"savefile name\n**{file_name}**\nhas not been claimed.\n" \
           "Create a character with the add_char command to claim it for yourself, make sure to write down the file's name"


def insert_into_file_dict(file_name: str, save_dict: dict):
    global file_dict
    if file_name in file_dict:
        file_dict[file_name][TIMER_LABEL].cancel()
        del file_dict[file_name]
    file_dict[file_name] = {
        TIMER_LABEL: get_file_mem_deletion_timer(file_name),
        SAVE_LABEL: save_dict
    }
    file_dict[file_name][TIMER_LABEL].start()


def get_file_dict_save(file_name: str):
    global file_dict
    load_file_into_memory(file_name)
    reset_file_timer(file_name)
    return file_dict[file_name][SAVE_LABEL]


def clear_file_dict_entry(file_name: str):
    global file_dict
    if file_name in file_dict:
        file_dict[file_name][TIMER_LABEL].cancel()
        del file_dict[file_name]
        logger.info(f"{file_name} WAS CLEARED FROM MEMORY")
    logger.info(str(file_dict))


def reset_file_timer(file_name: str):
    global file_dict
    if file_name in file_dict:
        file_dict[file_name][TIMER_LABEL].cancel()
        file_dict[file_name][TIMER_LABEL] = get_file_mem_deletion_timer(file_name)
        file_dict[file_name][TIMER_LABEL].start()
        logger.debug(f"{file_name}: File timer was reset")
    else:
        logger.warning(f"{file_name}: File timer could not be reset. File is not in memory")


def set_user_file_link(user_id: str, _file_name: str):
    global ID_dict

    if user_id in ID_dict:
        reset_user_timer(user_id)
        ID_dict[user_id][FILENAME_LABEL] = _file_name
    else:
        ID_dict[user_id] = {
            FILENAME_LABEL: _file_name,
            TIMER_LABEL: get_ID_deletion_timer(user_id)
        }
        ID_dict[user_id][TIMER_LABEL].start()


def clear_user_file_link(user_id: str):
    global ID_dict
    if user_id in ID_dict:
        ID_dict[user_id][TIMER_LABEL].cancel()
        del ID_dict[user_id]
        logger.info(f"{user_id} WAS CLEARED FROM MEMORY")

    logger.info(str(ID_dict))


def reset_user_timer(reset_id: str):
    global ID_dict
    if reset_id in ID_dict:
        ID_dict[reset_id][TIMER_LABEL].cancel()
        ID_dict[reset_id][TIMER_LABEL] = get_ID_deletion_timer(reset_id)
        ID_dict[reset_id][TIMER_LABEL].start()
        logger.debug(f"{reset_id}: user timer was reset")
    else:
        logger.warning(f"{reset_id}: user timer could not be reset. user is not in memory")


