import logging
from discord.ext import commands
from discord import ApplicationContext, option

from .BladesResources.ResourceLogic import ResourceView, send_stress_tracker
from .BladesResources.ResourceTracker import ResourceTracker
from ...ContextInfo import init_context
from ...command_helper_functions import bot_channel_permissions_check

logger = logging.getLogger('bot')


class ResourcesCog(commands.Cog):
    @commands.slash_command(name="stress", description="Start a new Stress track.")
    @option(name="start_stress", description="The amount of stress at the start")
    @option(name="max_stress", description="The length of the stress bar.")
    async def weather(self, ctx: ApplicationContext, start_stress: int = 0, max_stress: int = 9):
        if not await bot_channel_permissions_check(ctx):
            return

        stress_tracker = ResourceTracker(start_stress, max_stress)
        await send_stress_tracker(await init_context(ctx=ctx), stress_tracker)


def setup(bot: commands.Bot):
    # Every extension should have this function
    bot.add_cog(ResourcesCog())
    bot.add_view(ResourceView(ResourceTracker(0, 9)))
    logger.info("Resources extension loaded")
