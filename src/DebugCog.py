import logging
from discord.ext import commands, bridge
from discord.ext.bridge import BridgeExtContext
from . import GlobalVariables, command_helper_functions as hlp_f
from .extension_loading import load_extensions

logger = logging.getLogger('bot')


class DebugCog(commands.Cog):

    @commands.command(name="r")
    async def reload(self, ctx: BridgeExtContext):
        if not hlp_f.check_admin(ctx):
            await ctx.send("you are not authorized to use this command")
            logger.info(f"user {ctx.author.name} attempted to use reload command")
            return
        load_extensions(GlobalVariables.bot, reload=True)
        await ctx.send("reloaded")
        logger.info(f"user {ctx.author.name} reloaded bot")




def setup(bot: bridge.Bot):
    # Every extension should have this function
    bot.add_cog(DebugCog())
    logger.info("debug extension loaded\n")


