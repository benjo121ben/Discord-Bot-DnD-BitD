import os
from dotenv import load_dotenv
from src.Connector import start_connection
from src.GlobalVariables import charDic
import src.GlobalVariables as globalVars
from os.path import exists
from src.Game import *

save = None


def load(_save_name):
    if exists('saves/' + _save_name):
        print("Savefile exists")
        imported_dic = json.load(open('saves/' + _save_name))
        for char_name, char_data in imported_dic.items():
            charDic[char_name] = char_from_data(char_data)


def load_entanglements():
    if exists('Assets/Expanded_Entanglements.json'):
        globalVars.imported_expanded_entanglements = json.load(open('Assets/Expanded_Entanglements.json'))
        globalVars.entanglements_exist = True


def save(_save_name):
    if not exists('saves/' + _save_name):
        if not exists('saves'):
            os.mkdir("saves")
        print("created savefile")
    with open('saves/' + _save_name, 'w') as newfile:
        output = {}
        for char in charDic.values():
            temp = toJSON(char)
            output[temp['name']] = temp
        json.dump(output, newfile, sort_keys=True, indent=4)


def main():
    print("Discord_BOT startup")
    load_entanglements()
    print("Input savefile used")
    load_dotenv('.env')
    #load(input() + "_save.json") #removed json loading, not yet implemented
    print("token:", os.environ.get("DISCORD_TOKEN"))
    start_connection(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"))


main()

