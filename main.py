import discord
import os
from dotenv import load_dotenv
from src.Connector import start_connection
from os.path import exists
from src.Game import *

game_list = {}
save = None

def load_save_file():  # read in save.json in case the bot shut down
    if not exists('saves/gamesave.json'):
        if not exists('saves'):
            os.mkdir("saves")
        with open('saves/gamesave.json', 'w') as newfile:
            blank_json = {
                'gameList': []
            }
            json.dump(blank_json, newfile)

        print("created savefile")
        return

    print("Savefile exists")
    save = json.load(open('saves/gamesave.json'))


def main():
    load_dotenv('.env')
    load_save_file()
    start_connection(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"))


main()

