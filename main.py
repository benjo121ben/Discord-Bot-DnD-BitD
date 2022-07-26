import os
from dotenv import load_dotenv
from src.Bot_Setup import start_bot


def main():
    print("Discord_BOT startup")
    load_dotenv('.env')
    if os.environ.get("DISCORD_TOKEN") is None:
        print("TOKEN IS EMPTY.")
        print("restart the bot after inserting another token")
        return
    start_bot(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"))


main()
