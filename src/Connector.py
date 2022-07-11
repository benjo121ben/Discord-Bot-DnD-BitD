from discord.ext import commands
from .Game import *
import src.Commands

global game_list
bot = None


def start_connection(used_command_character, bot_token):
    global bot
    bot = commands.Bot(used_command_character)

    @bot.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(bot))

    @bot.event
    async def on_message(msg):
        if msg.author == bot.user:
            return
        print(msg)
        await msg.channel.send("test")

    bot.run(bot_token)


def check_for_game_name(name) -> bool:
    for game in game_list:
        if game.game_name == name:
            return True
    return False


def get_game_index(name):
    for i in range(0, len(game_list)):
        if game_list[i].game_name == name:
            return i
    raise Exception("game of this name does not exist: " + name)


def add_game(game_name: str, user_name: str) -> str:
    if check_for_game_name(game_name):
        return "Game by this name already exists."
    game_list.append(Game(game_name, user_name))
    return "created Game " + game_name


def add_player(game_name: str, command_user, player_username) -> str:
    index = get_game_index(game_name)
    return game_list[index].add_player(command_user, player_username)


def rem_player(game_name: str, command_user, player_username) -> str:
    index = get_game_index(game_name)
    return game_list[index].remove_player(command_user, player_username)


def add_char(game_name: str, command_user, player_name, char_name) -> str:
    index = get_game_index(game_name)
    return game_list[index].add_character(command_user, player_name, char_name)


def rem_char(game_name: str, command_user, char_name) -> str:
    index = get_game_index(game_name)
    return game_list[index].remove_character(command_user, char_name)
