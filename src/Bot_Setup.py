import asyncio
import logging
import discord
from src.ext.Campaign import packg_variables as c_var
from aiohttp import ClientConnectorError
from discord.ext import bridge

import src.ext.Campaign.packg_variables
from src import GlobalVariables, command_helper_functions as hlp_f

ext_base_path = "src.ext."
logger: logging.Logger = None


class MyInternetException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def start_bot(_command_prefix, _bot_token):
    global logger
    logger = logging.getLogger('bot')
    intents = discord.Intents.default()
    intents.message_content = True
    GlobalVariables.bot = bridge.Bot(command_prefix=_command_prefix, intents=intents)
    c_var.bot = GlobalVariables.bot
    load_extensions(GlobalVariables.bot)

    @GlobalVariables.bot.event
    async def on_ready():
        logger.info(f"Bot startup completed\n"
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
    GlobalVariables.bot.run(_bot_token)
    logger.warning("Bot start has somehow completed")


def load_extensions(_bot, reload=False):
    def load_ext(extension):
        if reload:
            _bot.reload_extension(ext_base_path + extension)
        else:
            _bot.load_extension(ext_base_path + extension)

    global logger
    logger.info("\n---------------------LOADING EXTENSIONS---------------------\n")
    load_ext("Campaign.CampaignCog")
    load_ext("Clocks.ClockCog")
    load_ext("BladesUtility.BladesUtilityCog")
    logger.info("---------------------EXTENSIONS LOADED---------------------\n")

