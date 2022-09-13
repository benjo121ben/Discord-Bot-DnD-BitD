import os
from src import GlobalVariables
from dotenv import load_dotenv
import requests

applicationID = 974306765686571088


def main(*args):
    load_dotenv('.env')
    print(args)
    if len(args) > 0 and args[0] == 'd':
        command_id = args[1]

        print("command deletion")
        load_dotenv('.env')
        url = f"https://discord.com/api/v10/applications/{applicationID}/commands/{command_id}"

        # For authorization, you can use either your bot token
        headers = {
            "Authorization": "Bot " + os.environ.get("DISCORD_TOKEN")
        }
        print(requests.delete(url, headers=headers))

    else:
        print("command setup")
        url = f"https://discord.com/api/v10/applications/{applicationID}/commands"

        # This is an example CHAT_INPUT or Slash Command, with a type of 1
        json = {
            "name": "cache",
            "type": 1,
            "description": "cache the latest saveFile",
            "options": [

                {
                    "name": "chat_id",
                    "description": "Whether to show only baby animals",
                    "type": 5,
                    "required": False
                }
            ]
        }

        # For authorization, you can use either your bot token
        headers = {
            "Authorization": "Bot " + os.environ.get("DISCORD_TOKEN")
        }

        print(requests.post(url, headers=headers, json=json))


main(*input("keyword input:\n").split(" "))
