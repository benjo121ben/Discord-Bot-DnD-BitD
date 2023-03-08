import os, pathlib
import shutil

from .test_const_vars import template_save_folder_relative_path, unit_test_save_file_name
from src.ext.Campaign.SaveDataManagement.save_file_management import save_files_suffix
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager, live_save_manager as live_manager
from src.ext.Campaign import Undo
this_file_folder_path = pathlib.Path(__file__).parent.resolve()


def get_template_path(template_name):
    return f"{os.path.join(this_file_folder_path, template_save_folder_relative_path)}{os.sep}{template_name}{save_files_suffix}"


def move_template_save_to_save_folder(template_name):
    source = get_template_path(template_name)
    if not os.path.exists(source):
        raise Exception("Invalid template path given")
    destination = save_manager.build_savefile_path(unit_test_save_file_name)
    shutil.copyfile(source, destination)
    return destination


def cleanup_template():
    Undo.reset_undo()
    live_manager.unload_all_files_and_users()
    save_manager.remove_save_file(unit_test_save_file_name)
