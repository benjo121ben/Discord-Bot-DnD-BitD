import logging

from .TempEntryDict import TempEntryDict
from ..Character import Character
from ..campaign_exceptions import NotFileAdminException, NoAssignedSaveException, UserNotPlayerException
from .save_file_management import save_file_to_parsed_dictionary, save_data_to_file, players_tag, character_tag, \
    create_fresh_save, setup_save_folders, admin_tag

USER_ID_DELETION_SECONDS = 10800
FILE_DELETION_SECONDS = 3600

ID_dict = TempEntryDict(USER_ID_DELETION_SECONDS, "ID")
file_dict = TempEntryDict(FILE_DELETION_SECONDS, "File")
logger = logging.getLogger('bot')


def setup_live_save_data():
    global ID_dict, file_dict
    setup_save_folders()
    ID_dict.clear()
    file_dict.clear()


def check_file_loaded(user_id: str, raise_error: bool = False) -> bool:
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


def get_loaded_filename(user_id: str) -> str:
    global ID_dict
    """
    Gets the filename assigned to a user
    :param user_id: the id of the user trying to access their savefile
    :return: The filename assigned to the user or None if no file was assigned
    """
    return ID_dict.get(user_id)


def get_loaded_dict(user_id: str) -> dict:
    global ID_dict, file_dict
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
    _save_name = ID_dict.get(user_id)
    if _save_name is None:
        raise NoAssignedSaveException()

    try:
        access_file_as_user(user_id, _save_name)
    except UserNotPlayerException:
        ID_dict.remove(user_id)
        raise UserNotPlayerException("It seems you had your access rights to this savefile removed.\n"
                                     "Please contact the admin of the savefile you are trying to access")

    return file_dict.get(_save_name)


def check_file_player(user_id: str, _save_name: str, raise_error=False) -> bool:
    global file_dict
    load_file_into_memory(_save_name)
    if user_id in file_dict.get(_save_name)[players_tag]:
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


def get_loaded_chars(user_id: str) -> dict[str, Character]:
    """
    Gets the character dictionary assigned to a user's save, or None if the user does not have an assigned savefile.\n
    If the file is not in memory, it will attempt to load the file from the drive.

    :param user_id: the user_id of the user trying to access
    :return: the save file dictionary
    :raises UserNotPlayerException: If the user is not authorized to access the file
    :raises SaveFileNotFoundException: If the savefile is not in memory and was deleted from the hardware
    """
    return get_loaded_dict(user_id)[character_tag]


def access_file_as_user(user_id: str, _save_name: str) -> str:
    global ID_dict
    check_file_player(user_id, _save_name, True)
    ID_dict.set(user_id, _save_name)
    return f"Savefile {_save_name} exists.\n Data loaded."


def save_user_file(user_id: str):
    file_name = get_loaded_filename(user_id)
    if file_name is not None:
        save_data_to_file(file_name, file_dict.get(file_name))
    else:
        raise Exception("save_user_file was called for a user that had no savefile assigned")


def load_file_into_memory(_file_name, replace=False):
    """
    Loads a file into memory if it was not already there

    :param _file_name: the save_name without suffix of the file that should be loaded
    :param replace:
    :return:
    """
    global file_dict
    if _file_name not in file_dict or replace:
        file_dict.set(_file_name, save_file_to_parsed_dictionary(_file_name))
        logger.debug(f"Loaded {_file_name} into meomory")
    else:
        logger.debug(f"{_file_name} accessed")


def unload_all_files_and_users():
    global file_dict, ID_dict
    file_dict.clear()
    ID_dict.clear()


def create_new_save(executing_user: str, file_name: str) -> str:
    """
    Creates a new save file in memory, which will be saved once the first character is added

    :param executing_user: the executing users id
    :param file_name: the save_name without suffix of the new save
    :return: The text that should be shown to the user
    """
    global file_dict, ID_dict
    logger.info("new save called")
    file_dict.set(file_name, create_fresh_save(executing_user))

    ID_dict.set(executing_user, file_name)
    return f"savefile name\n**{file_name}**\nhas not been claimed.\n" \
           "Create a character with the add_char command to claim it for yourself, make sure to write down the file's name"


def add_player_to_save(executing_user: str, new_user: str) -> str:
    check_file_admin(executing_user, raise_error=True)
    _dict = get_loaded_dict(executing_user)
    players: list[str] = _dict[players_tag]
    if new_user in players:
        return f"player {new_user} is already part of save_file {get_loaded_filename(executing_user)}"

    players.append(new_user)
    _dict[players_tag] = players
    ret = f"player {new_user} added to save_file {get_loaded_filename(executing_user)}"
    logger.info(ret)
    return ret


def rem_player_from_save(executing_user: str, rem_user: str) -> str:
    check_file_admin(executing_user, raise_error=True)
    _dict = get_loaded_dict(executing_user)
    players: list[str] = _dict[players_tag]
    if rem_user not in players:
        return f"player {rem_user} is not part of savefile {get_loaded_filename(executing_user)}"

    players.remove(rem_user)
    for char in get_loaded_chars(executing_user).values():
        if char.player == rem_user:
            char.set_player("")
    _dict[players_tag] = players
    ret = f"player {rem_user} removed from save_file {get_loaded_filename(executing_user)}"
    logger.info(ret)
    return ret

