import logging
import time

import discord
from discord.ext import bridge
from aiohttp import ClientConnectorError
from .ext.Campaign import packg_variables as c_var
from . import GlobalVariables, command_helper_functions as hlp_f

ext_base_path = "src.ext."
logger: logging.Logger = None
retry_connection = True


class MyInternetException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


async def start_bot(_command_prefix: str, _bot_token: str, modules_list: list[bool]):
    global logger, retry_connection
    logger = logging.getLogger('bot')
    intents = discord.Intents.default()
    intents.message_content = True
    GlobalVariables.bot = bridge.Bot(command_prefix=_command_prefix, intents=intents)
    c_var.bot = GlobalVariables.bot
    load_extensions(GlobalVariables.bot, modules_list)

    def stop_retrying():
        global retry_connection
        retry_connection = False

    @GlobalVariables.bot.event
    async def on_ready():
        stop_retrying()
        logger.info(f"Bot connection completed\n"
                    f"We have logged in as {GlobalVariables.bot.user}")

    @GlobalVariables.bot.command(name="r")
    async def reload(ctx):
        if not hlp_f.check_admin(ctx):
            await ctx.send("you are not authorized to use this command")
            logger.info(f"user {ctx.user} attempted to use reload command")
            return
        load_extensions(GlobalVariables.bot, reload=True)
        await ctx.send("reloaded")
        logger.info(f"user {ctx.user} reloaded bot")

    @GlobalVariables.bot.slash_command(name="ping")
    async def ping(ctx):
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


def load_extensions(_bot, modules_list: list[bool] = None, reload=False):
    def load_ext(extension):
        if reload:
            _bot.reload_extension(ext_base_path + extension)
        else:
            _bot.load_extension(ext_base_path + extension)

    global logger
    logger.info("\n---------------------LOADING EXTENSIONS---------------------\n")
    if modules_list is None:
        load_ext("Campaign.CampaignCog")
        load_ext("BladesUtility.BladesUtilityCog")
        load_ext("BladesUtility.ClockCog")
    else:
        if modules_list[0]:
            load_ext("Campaign.CampaignCog")
        if modules_list[1]:
            load_ext("BladesUtility.BladesUtilityCog")
            load_ext("BladesUtility.ClockCog")

    logger.info("---------------------EXTENSIONS LOADED---------------------\n")

