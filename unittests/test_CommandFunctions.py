from unittest import TestCase
from src.ext.Campaign import save_file_management as save_manager, CommandFunctions as commands


unit_test_save_file_name = "unit_test_save"


class TestCommandFunctions(TestCase):
    def setUp(self) -> None:
        if save_manager.check_savefile_existence(unit_test_save_file_name):
            save_manager.remove(unit_test_save_file_name)
            print("deleted existing unit test savefile")
        save_manager.load(unit_test_save_file_name)

    def tearDown(self) -> None:
        save_manager.remove(unit_test_save_file_name)

    def test_log(self):
        print(commands.add_char("test", "test", 20))
        print(commands.log())
        assert save_manager.check_savefile_existence(unit_test_save_file_name)
