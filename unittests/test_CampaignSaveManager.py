import json
import pytest
from src.ext.Campaign.Character import Character
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager, live_save_manager as live_manager
from .test_const_vars import unit_test_save_file_name, test_user_id
from .unit_test_template_manager import get_template_path, move_template_save_to_save_folder, cleanup_template


def compare_char_with_dic(character: Character, check_char_dic: dict):
    for tag, value in character.__dict__.items():
        assert check_char_dic[tag] == value


class TestCampaignSaveManager:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield "setup"
        cleanup_template()

    def test_load(self):
        template_file_name = "base_test_full"
        move_template_save_to_save_folder(template_file_name)
        live_manager.access_file_as_user(test_user_id, unit_test_save_file_name)
        assert live_manager.get_loaded_filename(test_user_id) == unit_test_save_file_name
        assert unit_test_save_file_name in live_manager.new_file_dict
        with open(get_template_path(template_file_name)) as file:
            file_dic = json.load(file)

        # check file stats
        loaded_dict = live_manager.get_loaded_dict(test_user_id)
        print(loaded_dict[save_manager.last_changed_tag])
        assert file_dic[save_manager.session_tag] == loaded_dict[save_manager.session_tag]
        assert save_manager.parse_date_time(file_dic[save_manager.last_changed_tag]) \
               == loaded_dict[save_manager.last_changed_tag]
        # check character stats
        char_dic = live_manager.get_loaded_chars(test_user_id)
        for tag, check_char_dic in file_dic[save_manager.character_tag].items():
            assert tag in char_dic
            compare_char_with_dic(char_dic[tag], check_char_dic)

    def test_upgrade_versioning(self):
        template_file_name = "old_vers_test_full"
        new_file_path = move_template_save_to_save_folder(template_file_name)
        live_manager.access_file_as_user(test_user_id,
                                         unit_test_save_file_name)  # since the file has an older version. This should upgrade the file to a new version
        assert live_manager.get_loaded_filename(test_user_id) == unit_test_save_file_name

        with open(get_template_path(template_file_name)) as orig_file:
            orig_file_dic = json.load(orig_file)
        with open(new_file_path) as new_file:
            new_file_dic = json.load(new_file)

        # check file stats
        t_last_change = save_manager.last_changed_tag
        t_session = save_manager.session_tag
        live_data_dict = live_manager.get_loaded_dict(test_user_id)
        assert orig_file_dic[t_session] == new_file_dic[t_session]
        assert orig_file_dic[t_session] == live_data_dict[t_session]
        assert not (save_manager.parse_date_time(orig_file_dic[t_last_change]) == live_data_dict[t_last_change])
        assert save_manager.parse_date_time(new_file_dic[t_last_change]) == live_data_dict[t_last_change]

        # check character stats
        new_file_chars = new_file_dic[save_manager.character_tag]
        live_char_data = live_manager.get_loaded_chars(test_user_id)
        for tag, loaded_char_dic in orig_file_dic[save_manager.character_tag].items():
            assert tag in live_char_data
            assert tag in new_file_chars
            compare_char_with_dic(live_char_data[tag], loaded_char_dic)
            compare_char_with_dic(live_char_data[tag], new_file_chars[tag])
