from discord.ext import commands
from discord import File
from .Game import *
import src.Commands
from random import seed
from datetime import datetime
from random import random

global game_list
bot = None
seed(datetime.now().timestamp())


def start_connection(_command_prefix, _bot_token):
    global bot
    bot = commands.Bot(_command_prefix)

    @bot.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(bot))

    @bot.command(name="db")
    async def devils_bargain(ctx, *args):
        if ctx.author == bot.user:
            return
        elif len(args) == 1 and args[0].isnumeric():
            amount = min(10, int(args[0]))
            file_list: list[File] = []
            for i in range(0, amount):
                file_list.append(get_devils_bargain())
            await ctx.send(files=file_list)
        else:
            await ctx.send(file=get_devils_bargain())

    bot.run(_bot_token)


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


def get_devils_bargain():
    rand = 1 + int(random() * (50 - 1))
    if rand < 10:
        rand = "0" + str(rand)
    return File("Assets/DevilsBargain-" + str(rand) + ".png")
