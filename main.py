import os
import time

from aiohttp.client_exceptions import ClientConnectorError

from src import GlobalVariables
from dotenv import load_dotenv
from src.Bot_Setup import start_bot, MyInternetException, close_bot


def main():
    print("Discord_BOT startup")
    execute = True
    tries = 10
    load_dotenv('.env')
    GlobalVariables.cache_folder = check_env_var_int("CLOUD_SAVE_CHANNEL")
    GlobalVariables.admin_id = check_env_var_int("ADMIN_ID")
    if GlobalVariables.admin_id is None:
        input("No admin assigned\nRestart the bot after assigning an administrator")
    if os.environ.get("DISCORD_TOKEN") == "":
        input("TOKEN IS EMPTY.\nrestart the bot after inserting another token")
        return
    while execute and tries > 0:
        execute = False
        try:
            start_bot(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"))
        except MyInternetException:
            print("could not establish connection, retry in 5 seconds")
            time.sleep(5.0)
            execute = True
            tries -= 1
        finally:
            close_bot()


def check_env_var_int(environment_tag: str) -> int:
    """
    This is a wrapper for environ.get, that returns an int with None instead of ""
    if the tag was written down but not assigned.

    :param environment_tag: the tag used in the environment file
    :return: returns the value if assigned, otherwise None
    """
    if os.environ.get(environment_tag) == "":
        return None
    elif os.environ.get(environment_tag) is None:
        return None
    else:
        return int(os.environ.get(environment_tag))


if __name__ == "__main__":
    main()
