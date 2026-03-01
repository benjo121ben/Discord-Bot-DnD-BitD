import pathlib

import discord
import os

campaign_env_file_rel_path = os.sep.join(['..', '..', '..', '.env'])

cache_folder: int = None
bot_admin_id: int = None
bot: discord.Bot = None
message_deletion_delay: int = 10


def get_save_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, os.sep.join(['..', '..', '..', 'saves']))


def get_cache_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, os.sep.join(['..', '..', '..', 'saves', 'cache']))
