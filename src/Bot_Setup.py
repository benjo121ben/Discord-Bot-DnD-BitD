import asyncio

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
        print("Bot startup completed")
        print('We have logged in as {0.user}'.format(GlobalVariables.bot))

    @GlobalVariables.bot.command(name="r")
    async def reload(ctx):
        if not hlp_f.check_admin(ctx):
            await ctx.send("you are not authorized to use this command")
            return
        load_extensions(GlobalVariables.bot, reload=True)
        await ctx.send("reloaded")

    print("starting up bot")
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(GlobalVariables.bot.start(_bot_token))
    except ClientConnectorError:
        print("ERROR RAISED_BOT_SETUP CLIENT ERROR")
        raise MyInternetException("could not connect to the servers")
    except Exception as e:
        print("ERROR RAISED; FIND ME IN BOT SETUP")
        print(e)
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
