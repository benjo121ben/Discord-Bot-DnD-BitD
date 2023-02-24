import os
import json
import pathlib
import shutil
import pytest
from src.ext.Campaign import save_file_management as save_manager, packg_variables as cvars
from src.ext.Campaign.Character import Character
from .test_const_vars import template_save_folder_relative_path, save_folder_relative_path, unit_test_save_file_name

this_file_folder_path = pathlib.Path(__file__).parent.resolve()


def get_template_path(template_name):
    return f"{os.path.join(this_file_folder_path, template_save_folder_relative_path)}{os.sep}{template_name}{save_manager.save_files_suffix}"


def get_save_path(save_name):
    return f"{os.path.join(this_file_folder_path, save_folder_relative_path)}{os.sep}{save_name}{save_manager.save_files_suffix}"


def compare_char_with_dic(character: Character, check_char_dic: dict):
    for tag, value in character.__dict__.items():
        assert check_char_dic[tag] == value


def move_template_save_to_save_folder(template_name):
    source = get_template_path(template_name)
    if not os.path.exists(source):
        raise Exception("Invalid template path given")
    destination = get_save_path(unit_test_save_file_name)
    shutil.copyfile(source, destination)
    return destination


class TestCampaignSaveManager():
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield "setup"
        save_manager.remove(unit_test_save_file_name)

    def test_load(self):
        template_file_name = "base_test_full"
        move_template_save_to_save_folder(template_file_name)
        save_manager.load(unit_test_save_file_name)
        assert save_manager.save_file_no_suffix == unit_test_save_file_name
        with open(get_template_path(template_file_name)) as file:
            file_dic = json.load(file)

        # check file stats
        assert file_dic[save_manager.session_tag] == cvars.imported_dic[save_manager.session_tag]
        assert save_manager.parse_date_time(file_dic[save_manager.last_changed_tag]) \
               == cvars.imported_dic[save_manager.last_changed_tag]
        # check character stats
        for tag, loaded_char_dic in file_dic[save_manager.character_tag].items():
            assert tag in cvars.charDic
            compare_char_with_dic(cvars.charDic[tag], loaded_char_dic)

    def test_upgrade_versioning(self):
        template_file_name = "old_vers_test_full"
        new_file_path = move_template_save_to_save_folder(template_file_name)
        save_manager.load(unit_test_save_file_name) # since the file has an older version. This should upgrade the file to a new version
        assert save_manager.save_file_no_suffix == unit_test_save_file_name

        with open(get_template_path(template_file_name)) as orig_file:
            orig_file_dic = json.load(orig_file)
        with open(new_file_path) as new_file:
            new_file_dic = json.load(new_file)

        # check file stats
        t_last_change = save_manager.last_changed_tag
        t_session = save_manager.session_tag
        assert orig_file_dic[t_session] == new_file_dic[t_session]
        assert orig_file_dic[t_session] == cvars.imported_dic[t_session]
        assert not (save_manager.parse_date_time(orig_file_dic[t_last_change]) == cvars.imported_dic[t_last_change])
        assert save_manager.parse_date_time(new_file_dic[t_last_change]) == cvars.imported_dic[t_last_change]

        # check character stats
        new_file_chars = new_file_dic[save_manager.character_tag]
        for tag, loaded_char_dic in orig_file_dic[save_manager.character_tag].items():
            assert tag in cvars.charDic
            assert tag in new_file_chars
            compare_char_with_dic(cvars.charDic[tag], loaded_char_dic)
            compare_char_with_dic(cvars.charDic[tag], new_file_chars[tag])





