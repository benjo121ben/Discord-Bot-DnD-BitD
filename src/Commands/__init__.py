from src.GlobalVariables import charDic
from .CommandFunctions import *


# the command used in order to execute all other commands
def execute_command(*args):
    _command_name = args[0]
    if _command_name in localCommDic.keys():
        localCommDic[_command_name](*args[1:])
    else:
        print("Command does not exist")


# all used commands need to be added to the dictionary in order
# to work
localCommDic = {
    'addC': add_char,
    'cause': cause_damage,
    'take': take_damage,
    'inc': increase_health,
    'heal': heal,
    'healm': heal_max,
    'log': log
}
