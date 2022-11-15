from dotenv import load_dotenv
import os
from os import mkdir
from os.path import exists
from typing import Optional
import pathlib

from discord.ext.bridge import BridgeExtContext

from . import packg_variables as p_vars
from .save_file_management import get_save_folder_filepath, get_cache_folder_filepath, check_file_loaded
from .packg_variables import charDic
from .campaign_exceptions import CommandException

from src import GlobalVariables


def check_file_admin(user_id: int) -> bool:
    if p_vars.bot_admin_id is None:
        return True
    else:
        return user_id == p_vars.bot_admin_id


def check_bot_admin(ctx: BridgeExtContext) -> bool:
    if p_vars.bot_admin_id is None:
        return True
    else:
        return ctx.author.id == p_vars.bot_admin_id


def get_bot():
    if GlobalVariables.bot is not None:
        return GlobalVariables.bot
    else:
        raise CommandException("get_bot tries to get an empty bot")


def check_if_user_has_char(user_id) -> bool:
    for char in charDic.values():
        if char.player == str(user_id):
            return True
    return False


def get_char_tag_by_id(user_id: int):
    if not check_if_user_has_char(user_id):
        raise CommandException("get_tag_by_id: attempted to get the character of an unassigned user")
    for char in charDic.values():
        if char.player == str(user_id):
            return char.tag


def get_char_name_by_id(user_id: int):
    if not check_if_user_has_char(user_id):
        raise CommandException("get_char_name_by_id: attempted to get the character of an unassigned user")
    for char in charDic.values():
        if char.player == str(user_id):
            return char.name


def check_char_tag(char_tag: str, raise_error: bool = False):
    """
    Checks if a character with this tag exists in the current save file
    :param char_tag: tag of checked character
    :param raise_error: If true, the function will throw a CommandException if the character was not found
    :return: True if character was found, False otherwise
    """
    if not check_file_loaded(raise_error=raise_error):
        return False
    if char_tag is None:
        if raise_error:
            raise CommandException(
                "campaign_helper:check_char_tag: Character tag None was given. "
                "This should never happen, please contact the developer."
            )
    elif char_tag in charDic.keys():
        return True
    elif raise_error:
        raise CommandException("Character doesn't exist")
    return False


def get_char_tag_if_none(ctx: BridgeExtContext, char_tag: str = None):
    if char_tag is not None:
        return char_tag

    check_file_loaded(raise_error=True)
    for char in charDic.values():
        if char.player == str(ctx.author.id):
            return char.tag
    raise CommandException(
        "No character is assigned to you. Either claim a character or add the char_tag as a parameter")


def get_module_env_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, p_vars.campaign_env_file_rel_path)


def check_base_setup():
    def check_env_var_int(environment_tag: str) -> Optional[int]:
        """
        This is a wrapper for environ.get, that returns an int with None instead of ""
        if the tag was written down but not assigned.

        :param environment_tag: the tag used in the environment file
        :return: returns the value if assigned, otherwise None
        """
        if os.environ.get(environment_tag) == "":
            return None
        elif os.environ.get(environment_tag) is None:
            return None
        else:
            return int(os.environ.get(environment_tag))

    load_dotenv(get_module_env_filepath())
    p_vars.cache_folder = check_env_var_int("CLOUD_SAVE_CHANNEL")
    p_vars.bot_admin_id = check_env_var_int("ADMIN_ID")
    if p_vars.bot_admin_id is None:
        input(
            "\nERROR:CAMPAIGN_EXTENSION: No admin assigned\n"
            "Restart the bot after assigning an administrator in the .env file\npress ENTER"
        )
        return

    if not exists(get_save_folder_filepath()):
        print("SAVE_FILEPATH_CREATED")
        mkdir(get_save_folder_filepath())
    if not exists(get_cache_folder_filepath()):
        print("CACHE_FILEPATH_CREATED")
        mkdir(get_cache_folder_filepath())


