from unittest import TestCase
from src.ext.Campaign import save_file_management as save_manager, CommandFunctions as commands
from decohints import decohints
from functools import wraps


unit_test_save_file_name = "unit_test_save"


def setup_test_file():
    if save_manager.check_savefile_existence(unit_test_save_file_name):
        save_manager.remove(unit_test_save_file_name)
        print("deleted existing unit test savefile")
    save_manager.load(unit_test_save_file_name)


def close_test_file():
    save_manager.remove(unit_test_save_file_name)


@decohints
def unit_test_save_file_wrapper(unit_test_to_wrap):
    @wraps(unit_test_to_wrap)
    def wrapped_func(*args, **kwargs):
        setup_test_file()
        value = unit_test_to_wrap(*args, **kwargs)
        close_test_file()
        return value
    return wrapped_func


class TestCommandFunctions(TestCase):
    @unit_test_save_file_wrapper
    def test_log(self):
        print(commands.add_char("test", "etst", 20))
        print(commands.log())
        assert save_manager.check_savefile_existence(unit_test_save_file_name)
