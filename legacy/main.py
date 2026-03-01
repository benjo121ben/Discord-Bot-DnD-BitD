import asyncio
import os
import pathlib

from src import GlobalVariables
from dotenv import load_dotenv
from src.Bot_Setup import start_bot
from src.bot_logging import setup_logging


def get_env_bool(environment_tag: str) -> bool:
    """
    This is a wrapper for environ.get, that returns a boolean
    if the tag was written down but not assigned.

    :param environment_tag: the tag used in the environment file
    :return: returns the value if assigned, otherwise None
    """
    value = os.environ.get(environment_tag)
    if value is not None:
        return value == "1"


def main():

    logger = setup_logging()
    logger.info("initializing")
    main_path = pathlib.Path(__file__).parent.resolve()
    load_dotenv(os.path.join(main_path, GlobalVariables.env_file_rel_path))
    GlobalVariables.admin_id = os.environ.get("ADMIN_ID")
    GlobalVariables.bot_host_email = os.environ.get("HOST_EMAIL")
    token = os.environ.get("DISCORD_TOKEN")
    if token is None or token == "":
        input("\nERROR:DISCORD_TOKEN IS EMPTY.\nrestart the bot after inserting a token into the .env file\npress ENTER")
        return

    loop = asyncio.new_event_loop()
    modules = [get_env_bool("DND"), get_env_bool("BLADES"), get_env_bool("KANKA"), get_env_bool("WEATHER")]
    try:
        loop.run_until_complete(start_bot(os.environ.get('COMMAND_CHAR'), os.environ.get("DISCORD_TOKEN"), modules))
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt")


if __name__ == "__main__":
    main()
