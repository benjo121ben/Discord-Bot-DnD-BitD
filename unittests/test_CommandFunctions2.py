import pytest

from src.ext.Campaign import CommandFunctions as commands
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager, live_save_manager as live_manager

from .test_const_vars import unit_test_save_file_name, test_user_id
from .unit_test_template_manager import move_template_save_to_save_folder, cleanup_template


class TestCommandFunctions:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        if save_manager.check_savefile_existence(unit_test_save_file_name):
            save_manager.remove_file(unit_test_save_file_name)
            live_manager.unload_all_files_and_users()
            print("deleted existing unit test savefile")
        commands.load_or_create_save(test_user_id, unit_test_save_file_name)
        print("setup done")
        yield "setup"
        cleanup_template()
        print("teardown done")

    def test_log(self):
        print(commands.add_char(test_user_id, "test", "test"))
        print(commands.log(test_user_id))
        assert save_manager.check_savefile_existence(unit_test_save_file_name)

