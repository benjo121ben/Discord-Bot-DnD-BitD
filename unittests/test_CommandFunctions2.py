import pytest

from src.ext.Campaign import CommandFunctions as commands
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager

from .test_const_vars import unit_test_save_file_name


class TestCommandFunctions:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        print("setup")
        if save_manager.check_savefile_existence(unit_test_save_file_name):
            save_manager.remove(unit_test_save_file_name)
            print("deleted existing unit test savefile")
        save_manager.load(unit_test_save_file_name)
        yield "setup"
        save_manager.remove(unit_test_save_file_name)
        print("teardown")

    def test_log(self):
        print(commands.add_char("test", "test", 20))
        print(commands.log())
        assert save_manager.check_savefile_existence(unit_test_save_file_name)

