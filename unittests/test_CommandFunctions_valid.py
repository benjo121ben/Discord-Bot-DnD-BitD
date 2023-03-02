import discord.ext.bridge
import pytest
import unittest.mock as mock
from src.ext.Campaign import CommandFunctions as commands
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager, live_save_manager as live_manager, char_data_access as char_access

from .test_const_vars import unit_test_save_file_name, test_user_id, test_char_tag, test_discord_username, \
    get_mocked_bot
from .unit_test_template_manager import move_template_save_to_save_folder, cleanup_template


class TestCommandFunctions:
    @pytest.fixture
    def create_save_and_delete(self):
        if save_manager.check_savefile_existence(unit_test_save_file_name):
            save_manager.remove_file(unit_test_save_file_name)
            cleanup_template()
            print("deleted existing unit test savefile")
        commands.load_or_create_save(test_user_id, unit_test_save_file_name)
        print("setup done")
        yield "setup"
        cleanup_template()
        print("teardown done")



    def test_create(self, create_save_and_delete):
        print(commands.add_char(test_user_id, test_char_tag, "test"))
        print(commands.log(test_user_id))
        assert save_manager.check_savefile_existence(unit_test_save_file_name)
        _char = char_access.get_char(test_user_id, test_char_tag)
        assert _char.name == "test"
        assert _char.tag == test_char_tag
        assert _char.player == ""
        assert _char.damage_caused == 0
        assert _char.damage_healed == 0
        assert _char.damage_resisted == 0
        assert _char.damage_taken == 0
        assert _char.max_damage == 0
        assert _char.faints == 0
        assert _char.kills == 0
        assert _char.crits == 0
        assert _char.dodged == 0

    def test_rename(self, create_save_and_delete):
        OLD_NAME = "TEST"
        NEW_NAME = "NEW_TEST_NAME"
        print(commands.add_char(test_user_id, test_char_tag, OLD_NAME))
        _char = char_access.get_char(test_user_id, test_char_tag)
        assert _char.name == OLD_NAME
        print(commands.rename_character(test_user_id, test_char_tag, NEW_NAME))
        assert _char.name != OLD_NAME
        assert _char.name == NEW_NAME

    def test_log(self, create_save_and_delete):
        print(commands.add_char(test_user_id, test_char_tag, "test"))
        print(commands.log(test_user_id))



