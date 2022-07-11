from helper_functions import *
import CommandException


# command usage: addG game_name
def add_game(context, messager_name, *args) -> str:
    _game_name = args[0]
    check_command_arg_len(1, args)
    if check_for_game_id(_game_name, context.game_list):
        raise CommandException.CommandException("A Game by this name already exists.")
    context.game_list[_game_name] = Game(_game_name, messager_name)
    return "created Game " + _game_name


# command usage: addP game_name added_player_username
def add_player(context, messager_name, override, *args) -> str:
    check_command_arg_len(2, args)
    _game_name, _added_player_username = args
    return context.game_list[_game_name].add_player(messager_name, _added_player_username)


# command usage: remP game_name added_player_username
def rem_player(context, messager_name, *args) -> str:
    check_command_arg_len(2, args)
    _game_name, _removed_player_username = args
    return context.game_list[_game_name].remove_player(messager_name, _removed_player_username)


# command usage: addC game_name player_name char_name
def add_char(context, messager_name, *args) -> str:
    check_command_arg_len(3, args)
    _game_name, _player_name, _char_name = args
    return context.game_list[_game_name].add_character(messager_name, _player_name, _char_name)


# command usage: remC game_name char_name
def rem_char(context, messager_name, *args) -> str:
    check_command_arg_len(2, args)
    _game_name, _char_name = args
    return context.game_list[_game_name].remove_character(messager_name, _char_name)
