import asyncio
import logging
from aiohttp import ClientConnectorError
from discord.ext import bridge
import discord
from src import GlobalVariables, command_helper_functions as hlp_f

ext_base_path = "src.ext."


class MyInternetException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def start_bot(_command_prefix, _bot_token):
    intents = discord.Intents.default()
    intents.message_content = True
    bot_loop = asyncio.get_event_loop()
    GlobalVariables.bot = bridge.Bot(command_prefix=_command_prefix, intents=intents, loop= bot_loop)
    load_extensions(GlobalVariables.bot)

    @GlobalVariables.bot.event
    async def on_ready():
        print(f"Bot startup completed\n"
              f"We have logged in as {GlobalVariables.bot.user}")

    @GlobalVariables.bot.command(name="r")
    async def reload(ctx):
        if not hlp_f.check_admin(ctx):
            await ctx.send("you are not authorized to use this command")
            logging.debug(f"user {ctx.user} attempted to use reload command")
            return
        load_extensions(GlobalVariables.bot, reload=True)
        await ctx.send("reloaded")
        logging.debug(f"user {ctx.user} reloaded bot")

    print("starting up bot")
    logging.debug("bot startup")
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(GlobalVariables.bot.start(_bot_token))
    except ClientConnectorError:
        logging.error("BOT_SETUP: ClientConnectorError. Raising MyInternetException")
        raise MyInternetException("could not connect to the servers")
    except Exception as e:
        logging.error(f"unexpected error raised in BOT_SETUP."
                      f"Error: {e}")
        raise e
    finally:
        loop.close()


def load_extensions(_bot, reload=False):
    def load_ext(extension):
        if reload:
            _bot.reload_extension(ext_base_path + extension)
        else:
            _bot.load_extension(ext_base_path + extension)

    print("\n---------------------LOADING EXTENSIONS---------------------\n")
    load_ext("Campaign.CampaignCog")
    load_ext("Clocks.ClockCog")
    load_ext("BladesUtility.BladesUtilityCog")
    print("---------------------EXTENSIONS LOADED---------------------\n")


def close_bot():
    loop2 = asyncio.new_event_loop()
    loop2.run_until_complete(GlobalVariables.bot.close())
    loop2.close()
