import os
import json
from json import JSONDecodeError
from os.path import exists
import pathlib
import logging

clocks_rel_save_path = os.sep.join(['..', 'saves', 'clock_saves'])
clock_save_suffix = '_clsave.json'

logger = logging.getLogger('bot')

clocks_dict_tag = "clocks"
version_tag = "v"
kanka_data_tag = "kanka"


def get_user_save_filepath(user_id: str) -> str:
    global clocks_rel_save_path, clock_save_suffix
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, os.sep.join([clocks_rel_save_path, user_id + clock_save_suffix]))


def load_user_dict(user_id: str) -> dict:
    if exists(get_user_save_filepath(user_id)):
        with open(get_user_save_filepath(user_id)) as file:
            try:
                imported_dic = json.load(file)
            except JSONDecodeError as e:
                logger.error(str(e))
                logger.error(f"user_id: {user_id}")
                raise Exception("An error has occured trying to parse JSON clock file")
        if version_tag in imported_dic:
            return imported_dic
        else:
            updated_dict = {clocks_dict_tag: imported_dic, version_tag: 1.0}
            save_user_dict(user_id, updated_dict)
            return updated_dict
    else:
        logger.info(f"Clock savefile doesn't exist, will create new savefile. User ID={user_id}")
        return {clocks_dict_tag: {}, version_tag: 1.0}


def save_user_dict(user_id: str, user_dict: dict):
    if len(user_dict) == 0 or (len(user_dict[clocks_dict_tag]) == 0 and kanka_data_tag not in user_dict):
        if exists(get_user_save_filepath(user_id)):
            os.remove(get_user_save_filepath(user_id))
        return

    if not exists(get_user_save_filepath(user_id)):
        path = ""
        for path_part in get_user_save_filepath(user_id).split(os.sep):
            path += path_part + os.sep
            if not exists(path) and ".json" not in path:
                os.mkdir(path)
        logger.info("created savefile")
    with open(get_user_save_filepath(user_id), 'w') as newfile:
        json.dump(user_dict, newfile, sort_keys=True, indent=4)

