import discord
import os
from dotenv import load_dotenv
from Connector import start_connection


def main():
    load_dotenv('.env')
    start_connection(os.environ.get('COMMAND_CHAR'), os.environ.get("TOKEN"))


main()

