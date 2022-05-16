import discord
from Game import *

commandChar = ''
client = discord.Client()
gameList: list[Game] = []


def start_connection(used_command_character, bot_token):
    global commandChar
    global client
    commandChar = used_command_character

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        try:
            await interpret_message(message)
        except Exception as e:
            await message.channel.send(e)

    client.run(bot_token)


async def interpret_message(message):
    global client
    return_message = ""
    if message.author == client.user:
        return

    if check_for_command(message, 'hello'):
        return_message = "hi"

    elif check_for_command(message, 'gametest add'):
        return_message = add_game("test game_name", message.author)

    elif check_for_command(message, 'playertest add'):
        return_message = add_player("test game_name", message.author, "benji2")

    elif check_for_command(message, 'playertest rem'):
        return_message = rem_player("test game_name", message.author, "benji2")

    elif check_for_command(message, 'chartest add'):
        return_message = add_char("test game_name", message.author, "Benjamin", "Fezim")

    elif check_for_command(message, 'chartest rem'):
        return_message = rem_char("test game_name", message.author, "Fezim")

    elif check_for_command(message, 'chartest altadd'):
        return_message = add_char("test game_name", "benji2", "Benjamin", "Vartha")

    elif check_for_command(message, 'chartest altrem'):
        return_message = rem_char("test game_name", "benji2", "Vartha")

    elif check_for_command(message, 'gameprint'):
        if len(gameList) != 0:
            for game in gameList:
                return_message += str(game)
        else:
            return_message += "there are no games to print"

    if return_message != "":
        await message.channel.send(return_message)


def check_for_command(message, command):
    global commandChar
    return message.content.startswith(commandChar + command)


def check_for_game_name(name) -> bool:
    for game in gameList:
        if game.game_name == name: return True
    return False


def get_game_index(name):
    for i in range(0, len(gameList)):
        if gameList[i].game_name == name: return i
    raise Exception("game of this name does not exist: " + name)


def add_game(game_name: str, user_name: str) -> str:
    if check_for_game_name(game_name):
        return "Game by this name already exists."
    gameList.append(Game(game_name, user_name))
    return "created Game " + game_name


def add_player(game_name: str, command_user, player_username) -> str:
    index = get_game_index(game_name)
    return gameList[index].add_player(command_user, player_username)


def rem_player(game_name: str, command_user, player_username) -> str:
    index = get_game_index(game_name)
    return gameList[index].remove_player(command_user, player_username)


def add_char(game_name: str, command_user, player_name, char_name) -> str:
    index = get_game_index(game_name)
    return gameList[index].add_character(command_user, player_name, char_name)


def rem_char(game_name: str, command_user, char_name) -> str:
    index = get_game_index(game_name)
    return gameList[index].remove_character(command_user, char_name)
