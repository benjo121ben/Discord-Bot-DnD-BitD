import logging

from discord.ext import commands
from discord import ApplicationContext, Embed
from ...command_helper_functions import channel_perm_check
from .ClockViews import SelectClockSizeView, ClockAdjustmentView
from .clock_data import load_clock_image_files

logger = logging.getLogger('bot')


class ClockCog(commands.Cog):

    @commands.slash_command(name="clock", description="creates a new clock")
    async def show_clock(self, ctx: ApplicationContext, clock_title: str):
        if not await channel_perm_check(ctx):
            return
        embed = Embed()
        embed.title = clock_title
        embed.description = "Select a size for your clock"
        embed.set_footer(text="Custom clock sizes unfortunately have no fancy images")
        view = SelectClockSizeView(clock_title)
        await ctx.respond("", embed=embed, view=view)


def setup(bot: commands.Bot):
    # Every extension should have this function
    load_clock_image_files()
    bot.add_view(SelectClockSizeView())
    bot.add_view(ClockAdjustmentView())
    bot.add_cog(ClockCog())
    logger.info("clock extension loaded")
