import logging
import time

from discord.ext import commands
from discord import ApplicationContext
from aiohttp import ClientConnectorError

from .ext.Campaign import packg_variables as c_var
from .ext.Clocks.ClockCog import LockedClockAdjustmentView
from .extension_loading import load_extensions
from . import GlobalVariables

logger: logging.Logger = None
retry_connection = True


class MyInternetException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


async def start_bot(_command_prefix: str, _bot_token: str, modules_list: list[bool]):
    global logger, retry_connection
    logger = logging.getLogger('bot')
    GlobalVariables.bot = commands.Bot(command_prefix=_command_prefix)
    c_var.bot = GlobalVariables.bot
    load_extensions(GlobalVariables.bot, modules_list)

    def stop_retrying():
        global retry_connection
        retry_connection = False

    @GlobalVariables.bot.event
    async def on_ready():
        stop_retrying()
        GlobalVariables.bot.add_view(LockedClockAdjustmentView("", ""))
        logger.info(f"Bot connection completed\n"
                    f"We have logged in as {GlobalVariables.bot.user}")

    @GlobalVariables.bot.slash_command(name="ping", description="Tests whether the bot is active")
    async def ping(ctx: ApplicationContext):
        await ctx.respond("pong")

    logger.info("attempting bot startup")
    counter = 30
    while retry_connection and counter > 0:
        try:
            await GlobalVariables.bot.start(_bot_token, reconnect=True)
        except ClientConnectorError as e:
            logger.error("Connector Error: " + str(e))
            counter -= 1
        except Exception as e:
            logger.error("Exception: " + str(e))
        finally:
            time.sleep(20)

    logger.warning("Bot start has somehow completed")


