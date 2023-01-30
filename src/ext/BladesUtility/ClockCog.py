import logging
from discord.ext import commands
from discord.ext import bridge
from discord import slash_command
from .clocks import NoClockImageException, clocks_save_dic, save_clocks, Clock, load_clocks


logger = logging.getLogger('bot')


async def print_clock(ctx, clock):
    try:
        await ctx.respond("**" + clock.name + "**", file=clock.get_embed_info()[1])
    except NoClockImageException as err:
        await ctx.respond("Clocks of this size have missing output images\n**"
                          + str(clock) + "**")
        logger.info(
            "clock of size ",
            str(clock.size),
            "was printed without image, make sure images are included for all clocks needed."
        )


class ClockCog(commands.Cog):

    @commands.slash_command(name="add_clock", description="Adds a new clock of a certain size.")
    async def add_clock(self, ctx, clock_name: str, clock_size: int, clock_ticks: int = 0):
        if clock_name in clocks_save_dic:
            await ctx.respond(content="This clock already exists!\n")
            await print_clock(ctx, clocks_save_dic[clock_name])
        else:
            clocks_save_dic[clock_name] = Clock(clock_name, clock_size, clock_ticks)
            save_clocks()
            await ctx.respond("Clock created")
            await print_clock(ctx, clocks_save_dic[clock_name])

    @commands.slash_command(name="remove_clock", description="Removes the selected saved clock")
    async def remove_clock(self, ctx, clock_name: str):
        if clock_name in clocks_save_dic:
            del clocks_save_dic[clock_name]
            save_clocks()
            await ctx.respond(content="The clock has been deleted!\n")
        else:
            await ctx.respond("Clock does not exist: " + clock_name)

    @commands.slash_command(name="show_clock", description="Prints a saved clock, with picture if possible")
    async def show_clock(self, ctx, clock_name):

        if clocks_save_dic.__contains__(clock_name):
            await print_clock(ctx, clocks_save_dic[clock_name])
        else:
            await ctx.respond("This clock does not exist")

    @commands.slash_command(name="all_clocks", description="Prints out all saved clocks")
    async def all_clocks(self, ctx):
        names = "These are the clocks that exist:\n"
        for name in clocks_save_dic.keys():
            names += name + "\n"
        await ctx.respond(names)

    @commands.slash_command(name="tick", description="Ticks the selected clock by a selected amount. Default: 1 tick")
    async def tick_clock(self, ctx, clock_name: str, ticks: int = 1):
        clock = clocks_save_dic.get(clock_name)
        if clock:
            clock.tick(ticks)
            save_clocks()
            await print_clock(ctx, clock)


def setup(bot: bridge.Bot):
    # Every extension should have this function
    load_clocks()
    bot.add_cog(ClockCog())

    logger.debug("clock extension loaded\n")
