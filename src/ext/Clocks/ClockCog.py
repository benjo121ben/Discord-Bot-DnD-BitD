import logging
from functools import wraps

from discord.ext import commands
from discord import ApplicationContext, Member

from .ClockViews import get_clock_response_params
from ... import GlobalVariables as global_vars
from .MessageContent.AbstractMessageContent import AbstractMessageContent
from .clock_data import load_clock_files, load_clocks
from .clock_logic import add_clock_command_logic, show_clock_command_logic, \
    MESSAGE_DELETION_DELAY
from ...ContextInfo import init_context_with_executing_user

logger = logging.getLogger('bot')


def executing_user_message_data_wrapper(ctx: ApplicationContext, function_to_wrap):
    """
    Decorator for all functions that require the opening of a context and execution of the function using the id of the
    user opening the context

    :param function_to_wrap: the function that is called
    :return: wrapped function
    """

    @wraps(function_to_wrap)
    async def wrapped_func(_function_to_wrap):
        context, executing_user = await init_context_with_executing_user(ctx=ctx)
        content: AbstractMessageContent = _function_to_wrap(executing_user=executing_user)
        await context.respond(**content.get_message_content(get_clock_response_params))
    return wrapped_func(function_to_wrap)


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

    @commands.slash_command(name="clock_add", description="Adds a new clock of a certain size.")
    async def add_clock(self, ctx: ApplicationContext, clock_tag: str, clock_title: str, clock_size: int, clock_ticks: int = 0):
        if not await self.bot_channel_permissions_check(ctx):
            return
        await executing_user_message_data_wrapper(
            ctx,
            lambda executing_user: add_clock_command_logic(clock_tag, clock_title, clock_size, executing_user, clock_ticks)
        )

    @commands.slash_command(name="clock", description="Prints a saved clock, with picture if possible")
    async def show_clock(self, ctx: ApplicationContext, clock_tag: str):
        if not await self.bot_channel_permissions_check(ctx):
            return
        await executing_user_message_data_wrapper(
            ctx,
            lambda executing_user: show_clock_command_logic(clock_tag, executing_user)
        )

    @commands.slash_command(name="clock_all", description="Prints out all saved clocks")
    async def all_clocks(self, ctx: ApplicationContext):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if len(clock_dic) == 0:
            await ctx.respond("You have no existing clock. use the **clock_add** command to create clocks.", delete_after=MESSAGE_DELETION_DELAY)
            return

        all_c = "These are the clocks that you have created:\n"
        for clock in clock_dic.values():
            all_c += str(clock) + "\n"
        await ctx.respond(all_c, delete_after=40)


def setup(bot: commands.Bot):
    # Every extension should have this function
    load_clock_files()
    bot.add_cog(ClockCog())
    logger.info("clock extension loaded")
