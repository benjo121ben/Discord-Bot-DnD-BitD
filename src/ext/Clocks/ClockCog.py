import logging

from discord.ext import commands
from discord import ApplicationContext, Member, Embed

from .ClockViews import SelectClockSizeView
from ... import GlobalVariables as global_vars
from .clock_data import load_clock_image_files
from .clock_logic import MESSAGE_DELETION_DELAY

logger = logging.getLogger('bot')


class ClockCog(commands.Cog):

    @staticmethod
    async def bot_channel_permissions_check(ctx: ApplicationContext):
        if ctx.guild is None:
            return True

        member_data: Member = ctx.guild.get_member(global_vars.bot.user.id)
        if not ctx.channel.permissions_for(member_data).view_channel:
            await ctx.respond("The bot does not have permission to view this channel.\n"
                              "Some stuff just doesn't work without it, so please make sure you give it access. :)",
                              delete_after=MESSAGE_DELETION_DELAY
                              )
            return False
        return True

    @commands.slash_command(name="clock", description="creates a new clock")
    async def show_clock(self, ctx: ApplicationContext, clock_title: str):
        if not await self.bot_channel_permissions_check(ctx):
            return
        embed = Embed()
        embed.title = clock_title
        view = SelectClockSizeView(clock_title)
        await ctx.respond("select size", view=view)


def setup(bot: commands.Bot):
    # Every extension should have this function
    load_clock_image_files()
    bot.add_view(SelectClockSizeView())
    bot.add_cog(ClockCog())
    logger.info("clock extension loaded")
