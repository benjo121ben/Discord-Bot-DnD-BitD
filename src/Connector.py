import discord
from discord.ext import commands
from discord import File
from .Game import *
import src.Commands
import src.GlobalVariables as globalVars
from .Entanglement_table import *
from random import seed
from random import random
from datetime import datetime

game_list ={}
bot = None
seed(datetime.now().timestamp())


def start_connection(_command_prefix, _bot_token):
    global bot
    bot = commands.Bot(_command_prefix)

    @bot.event
    async def on_ready():
        print("looking for entanglements")
        for col in range(0, 3):
            for i in range(0, 6):
                ent_list = Entanglement_sorting_table[col][i]
                for entanglement in ent_list:
                    if not globalVars.imported_expanded_entanglements.__contains__(entanglement):
                        globalVars.entanglements_exist = False
                        print("missing", entanglement)
        if not globalVars.entanglements_exist:
            print("Entanglements disabled, due to missing entanglements.")
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

    @bot.command(name="ent")
    async def entanglements(ctx, rolled: int, heat: int):
        if ctx.author == bot.user:
            return
        if not globalVars.entanglements_exist:
            ctx.send("Entanglements are missing, therefore this command was automatically deactivated.")
        column = -1
        if heat <= 3:
            column = 0
        elif heat <= 5:
            column = 1
        else:
            column = 2

        if rolled < 1 or rolled > 6:
            ctx.send("The number rolled has to be between 1 and 6")
            return
        rolled -= 1
        ent_list = Entanglement_sorting_table[column][rolled]
        embed = discord.Embed(title="Entanglements", description="choose one!")
        for entanglement in ent_list:
            embed.add_field(name=entanglement, value=globalVars.imported_expanded_entanglements[entanglement], inline=True)
        await ctx.send(embed=embed)

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
