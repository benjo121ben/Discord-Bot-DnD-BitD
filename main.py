import os
import time
import pathlib

from typing import Optional
from src import GlobalVariables
from dotenv import load_dotenv
from src.Bot_Setup import start_bot, MyInternetException, close_bot
from src.logging import setup_logging


def check_env_var_int(environment_tag: str) -> Optional[int]:
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


def main():

    logger = setup_logging()
    logger.info("initializing")
    execute = True
    tries = 10
    main_path = pathlib.Path(__file__).parent.resolve()
    load_dotenv(os.path.join(main_path, GlobalVariables.env_file_rel_path))
    GlobalVariables.admin_id = check_env_var_int("ADMIN_ID")
    token = os.environ.get("DISCORD_TOKEN")
    if token is None or token == "":
        input(
            "\nERROR:DISCORD_TOKEN IS EMPTY.\nrestart the bot after inserting a token into the .env file\npress ENTER")
        return
    while execute and tries > 0:
        execute = False
        try:
            start_bot(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"))
        except MyInternetException as e:
            logger.warning(f"MyInternetException raised. program retrying to establish connection.\n"
                           f"[TRIES LEFT= {tries-1}]\nError: {e}")
            time.sleep(5.0)
            execute = True
            tries -= 1
        finally:
            close_bot()
            logger.error("BOT TERMINATED")


if __name__ == "__main__":
    main()
