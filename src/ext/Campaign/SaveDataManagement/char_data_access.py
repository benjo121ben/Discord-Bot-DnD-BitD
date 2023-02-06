from .live_save_manager import check_file_loaded, get_user_loaded_chars, get_user_loaded_dict
from .save_file_management import character_tag
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
            raise CommandException(
                "campaign_helper:check_char_tag: Character tag None was given. "
                "This should never happen, please contact the developer."
            )
    elif char_tag in get_user_loaded_chars(executing_user):
        return True
    elif raise_error:
        raise CommandException("Character doesn't exist")
    return False


def get_char_tag_by_id(executing_user: str, search_user_id: str = None) -> str:
    if search_user_id is None:
        search_user_id = executing_user
    check_file_loaded(executing_user, raise_error=True)
    for char in get_user_loaded_chars(search_user_id).values():
        if char.player == search_user_id:
            return char.tag
    raise CommandException("This user does not have an assigned character")


def get_char_name_by_id(executing_user: str, search_user_id: str):
    if not check_if_user_has_char(executing_user, search_user_id):
        raise CommandException("This user does not have an assigned character")
    for char in get_user_loaded_chars(executing_user).values():
        if char.player == str(search_user_id):
            return char.name


def retag_char(executing_user: str, char_tag_old: str, char_tag_new: str):
    save_dic = get_user_loaded_dict(executing_user)
    save_dic[character_tag][char_tag_new] = save_dic[character_tag][char_tag_old]
    save_dic[character_tag][char_tag_new].tag = char_tag_new
    del save_dic[character_tag][char_tag_old]


def check_if_user_has_char(executing_user: str, search_user_id: str) -> bool:
    for char in get_user_loaded_chars(executing_user).values():
        if char.player == search_user_id:
            return True
    return False
