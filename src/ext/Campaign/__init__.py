from .CommandFunctions import setup_commands
from .packg_variables import localCommDic
from ..command_exceptions import CommandException


setup_commands()


# the command used in order to execute all other commands
def execute_command(*args) -> str:
    _command_name = args[0]
    if _command_name in localCommDic.keys():
        try:
            return localCommDic[_command_name](*args[1:])
        except CommandException as err:
            return str(err)

    else:
        return "Command does not exist"





