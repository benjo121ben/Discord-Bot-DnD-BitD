from src.GlobalVariables import charDic
from ..command_exceptions import *


# This checks in case of missing parameters or invalid amounts. does not cover multiple versions of same Command
def check_command_arg_len(supposed_len, *args):
    if len(args) != supposed_len:
        raise InvalidArgumentAmountException(supposed_len)
    return True


# is there to avoid functions being called on a character that doesn't exist
def check_char_name(char_name):
    if char_name in charDic.keys():
        return True
    else:
        raise Exception("Character doesn't exist")
