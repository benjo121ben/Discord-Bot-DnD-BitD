from constants import *
from game_functions import *


command_list = {
    constants.COM_ADD_GAME: add_game,
    constants.COM_ADD_PLAYER: add_player,
    constants.COM_REM_PLAYER: rem_player
}


def execute_commmand(command_id, context, messager_name, override = False, *args):
    command_list[command_id](context, messager_name, *args)



