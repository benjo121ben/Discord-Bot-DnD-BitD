import datetime
import logging
from discord import ApplicationContext
from discord.ext import commands, tasks
from . import GlobalVariables, bot_logging

logger = logging.getLogger('bot')
started_task = False


class DebugCog(commands.Cog):

    def __init__(self):
        global started_task
        logger.debug("DebugCog constructor called, tried to start task again")
        if not started_task:
            started_task = True
            self.reset_logger_handlers.start()

    @commands.slash_command(name="help", description="receive help with this bot")
    async def help(self, ctx: ApplicationContext):
        await ctx.respond(f"Any bugs, issues or ideas for improvements? Contact my creator on the support discord or via email\n"
                          f"Discord: https://discord.gg/fcJ7tQW9Ps\n" + \
                          (f"Email of bot-host: **{GlobalVariables.bot_host_email}**\n" if GlobalVariables.bot_host_email is not None else "") + \
                          f"Buy my creator a coffee: https://ko-fi.com/benjiwenger\n")

    @commands.slash_command(name="commands", description="get the command list")
    async def commands(self, ctx: ApplicationContext):
        await ctx.respond(f"See my commands here\nhttps://github.com/benjo121ben/Discord-Bot-DnD-BitD/blob/master/README.md#commands\n\n")

    # @commands.command(name="r")
    # async def reload(self, ctx: ApplicationContext):
    #     if not hlp_f.check_admin(ctx):
    #         await ctx.send("you are not authorized to use this command")
    #         logger.info(f"user {ctx.author.name} attempted to use reload command")
    #         return
    #     load_extensions(GlobalVariables.bot, reload=True)
    #     await ctx.send("reloaded")
    #     logger.info(f"user {ctx.author.name} reloaded bot")

    @tasks.loop(time=datetime.time(hour=0, minute=1, tzinfo=datetime.timezone(datetime.timedelta(hours=1))), reconnect=False)
    async def reset_logger_handlers(self):
        try:
            bot_logging.restart_logging()
            logger.debug("Logger restarted as scheduled")
            user = await GlobalVariables.bot.fetch_user(int(GlobalVariables.admin_id))
            await user.send("logger scheduled restart")
        except Exception as e:
            logger.error("an error occurred during the attempted restart")
            logger.error(e)


def setup(bot: commands.Bot):
    # Every extension should have this function
    bot.add_cog(DebugCog())
    logger.info("debug extension loaded")


