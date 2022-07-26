from src.GlobalVariables import charDic
from ..command_exceptions import *


def check_command_arg_len(min, *args, throw_error=True):
    return check_command_arg_len(min, -1, *args, throw_error)


# This checks in case of missing parameters or invalid amounts. does not cover multiple versions of same Command
def check_command_arg_len(min, max, *args, throw_error=True):
    if max != -1 and len(args) > max:
        if throw_error:
            raise TooManyArgumentsException(max)
    elif len(args) < min:
            return False
    return True


# is there to avoid functions being called on a character that doesn't exist
def check_char_name(char_name):
    if char_name in charDic.keys():
        return True
    else:
        raise CommandException("Character doesn't exist")
