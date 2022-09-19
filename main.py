import os
from src import GlobalVariables
from dotenv import load_dotenv
from src.Bot_Setup import start_bot


def main():
    print("Discord_BOT startup")
    load_dotenv('.env')
    GlobalVariables.cache_folder = check_env_var_int("CLOUD_SAVE_CHANNEL")
    GlobalVariables.admin_id = check_env_var_int("ADMIN_ID")
    if os.environ.get("DISCORD_TOKEN") == "":
        print("TOKEN IS EMPTY.")
        print("restart the bot after inserting another token")
        return
    start_bot(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"))


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


main()
