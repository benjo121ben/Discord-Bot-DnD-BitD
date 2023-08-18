import logging
from discord import ApplicationContext
from discord.ext import commands
from . import GlobalVariables

logger = logging.getLogger('bot')


class DebugCog(commands.Cog):

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




def setup(bot: commands.Bot):
    # Every extension should have this function
    bot.add_cog(DebugCog())
    logger.info("debug extension loaded\n")


