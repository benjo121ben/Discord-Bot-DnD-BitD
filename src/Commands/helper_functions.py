from ..Game import *
import CommandException


def check_command_arg_len(supposed_len, *args):
    if len(args) != supposed_len:
        raise CommandException.CommandArgAmountException(supposed_len)


# this takes a dict. Not 100% that's the right thing
def check_for_game_id(game_id, game_list: dict) -> bool:
    return game_list.__contains__(game_id)


