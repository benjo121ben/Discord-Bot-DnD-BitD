import logging
from discord.ext import commands
from discord.ext import bridge
from discord import slash_command
from .clocks import NoClockImageException, load_clock_files, save_clocks, Clock, load_clocks


logger = logging.getLogger('bot')


async def print_clock(ctx, clock):
    try:
        await ctx.respond("**" + clock.name + "**", file=clock.get_embed_info()[1])
    except NoClockImageException:
        await ctx.respond("Clocks of this size have missing output images\n**"
                          + str(clock) + "**")
        logger.debug(
            "clock of size " +
            str(clock.size) +
            " was printed without image, make sure images are included for all clocks needed."
        )


class ClockCog(commands.Cog):

    @commands.slash_command(name="add_clock", description="Adds a new clock of a certain size.")
    async def add_clock(self, ctx, clock_name: str, clock_size: int, clock_ticks: int = 0):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if clock_name in clock_dic:
            await ctx.respond(content="This clock already exists!\n")
            await print_clock(ctx, clock_dic[clock_name])
        else:
            clock_dic[clock_name] = Clock(clock_name, clock_size, clock_ticks)
            save_clocks(user_id, clock_dic)
            await ctx.respond("Clock created")
            await print_clock(ctx, clock_dic[clock_name])

    @commands.slash_command(name="remove_clock", description="Removes the selected saved clock")
    async def remove_clock(self, ctx, clock_name: str):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if clock_name in clock_dic:
            del clock_dic[clock_name]
            save_clocks(user_id, clock_dic)
            await ctx.respond(content="The clock has been deleted!\n")
        else:
            await ctx.respond("Clock does not exist: " + clock_name)

    @commands.slash_command(name="show_clock", description="Prints a saved clock, with picture if possible")
    async def show_clock(self, ctx, clock_name):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if clock_name in clock_dic:
            await print_clock(ctx, clock_dic[clock_name])
        else:
            await ctx.respond("This clock does not exist")

    @commands.slash_command(name="all_clocks", description="Prints out all saved clocks")
    async def all_clocks(self, ctx):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if len(clock_dic) == 0:
            await ctx.respond("You have no existing clock. use the add command to create clocks.")
            return

        all_c = "These are the clocks that exist:\n"
        for clock in clock_dic.values():
            all_c += str(clock) + "\n"
        await ctx.respond(all_c)

    @commands.slash_command(name="tick", description="Ticks the selected clock by a selected amount. Default: 1 tick")
    async def tick_clock(self, ctx, clock_name: str, ticks: int = 1):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        clock = clock_dic.get(clock_name)
        if clock:
            clock.tick(ticks)
            save_clocks(user_id, clock_dic)
            await print_clock(ctx, clock)
        else:
            await ctx.respond(f"No clock by the name {clock_name} was found.")


def setup(bot: bridge.Bot):
    # Every extension should have this function
    load_clock_files()
    bot.add_cog(ClockCog())
    logger.info("clock extension loaded\n")
