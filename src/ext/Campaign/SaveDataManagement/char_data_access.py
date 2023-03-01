from .live_save_manager import check_file_loaded, get_loaded_chars, get_loaded_dict
from .save_file_management import character_tag
from ..Character import Character
from ...command_exceptions import CommandException


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
            raise Exception(
                "campaign_helper:check_char_tag: Character tag None was given. "
                "This should never happen, please contact the developer."
            )
    elif char_tag in get_loaded_chars(executing_user):
        return True
    elif raise_error:
        raise CommandException("Character doesn't exist")
    return False


def get_char_tag_by_id(executing_user: str, search_user_id: str = None) -> str:
    if search_user_id is None:
        search_user_id = executing_user
    check_file_loaded(executing_user, raise_error=True)
    for char in get_loaded_chars(search_user_id).values():
        if char.player == search_user_id:
            return char.tag
    raise CommandException("This user does not have an assigned character")


def get_char_name_by_id(executing_user: str, search_user_id: str) -> str:
    for char in get_loaded_chars(executing_user).values():
        if char.player == str(search_user_id):
            return char.name
    raise CommandException("This user does not have an assigned character")


def get_char(user_id: str, char_tag: str) -> Character:
    """
    Gets a character from a loaded savefile

    :param user_id: the user_id of the user trying to access
    :param char_tag: the character tag associated with the appropriate character
    :return: the save file dictionary
    :raises UserNotPlayerException: If the user is not authorized to access the file
    :raises SaveFileNotFoundException: If the savefile is not in memory and was deleted from the hardware
    """
    _char_dict: dict[str, Character] = get_loaded_chars(user_id)
    if char_tag not in _char_dict:
        raise CommandException("Character doesn't exist")
    else:
        return _char_dict[char_tag]


def check_if_user_has_char(executing_user: str, search_user_id: str) -> bool:
    for char in get_loaded_chars(executing_user).values():
        if char.player == search_user_id:
            return True
    return False
