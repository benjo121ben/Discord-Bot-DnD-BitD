import logging

from dotenv import load_dotenv
import os
from os import mkdir
from os.path import exists
from typing import Optional
import pathlib

from discord.ext.bridge import BridgeExtContext

from . import packg_variables as p_vars
from .save_file_management import get_save_folder_filepath, get_cache_folder_filepath, check_file_loaded
from .campaign_exceptions import CommandException, NotBotAdminException, NotFileAdminException

logger = logging.getLogger('bot')



def check_bot_admin(ctx: BridgeExtContext, raise_error=False) -> bool:
    if p_vars.bot_admin_id is None or ctx.author.id == p_vars.bot_admin_id:
        return True
    elif raise_error:
        raise NotBotAdminException()
    else:
        return False


def get_bot():
    if p_vars.bot is not None:
        return p_vars.bot
    else:
        raise Exception("Campaign: get_bot tries to get an empty bot")


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
        logger.debug("SAVE_FILEPATH_CREATED")
        mkdir(get_save_folder_filepath())
    if not exists(get_cache_folder_filepath()):
        logger.debug("CACHE_FILEPATH_CREATED")
        mkdir(get_cache_folder_filepath())


