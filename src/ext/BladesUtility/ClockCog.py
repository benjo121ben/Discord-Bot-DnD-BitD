import logging
from discord.ext import commands, bridge
from discord import Embed, File
from .clocks import NoClockImageException, load_clock_files, save_clocks, Clock, load_clocks, get_clock_image


logger = logging.getLogger('bot')


async def print_clock(ctx, clock: Clock):
    embed = Embed(title=f'**{clock.name}**')
    try:

        image_file: File = get_clock_image(clock)
        embed.set_thumbnail(url=f'attachment://{image_file.filename}')
        await ctx.respond(embed=embed, file=image_file)
    except NoClockImageException:
        embed.set_footer(text="Clocks of this size don't have output images")
        embed.description = str(clock)
        await ctx.respond(embed=embed)
        logger.debug(
            f"clock of size {clock.size} was printed without image, make sure images are included for all sizes needed."
        )


class ClockCog(commands.Cog):

    @commands.slash_command(name="clock_add", description="Adds a new clock of a certain size.")
    async def add_clock(self, ctx, clock_name: str, clock_size: int, clock_ticks: int = 0):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if len(clock_dic) == 30:
            await ctx.respond("You already have 30 clocks, please remove one.")
            return

        if clock_name in clock_dic:
            await ctx.respond(content="This clock already exists!")
            await print_clock(ctx, clock_dic[clock_name])
        else:
            clock_dic[clock_name] = Clock(clock_name, clock_size, clock_ticks)
            save_clocks(user_id, clock_dic)
            await ctx.respond("Clock created")
            await print_clock(ctx, clock_dic[clock_name])

    @commands.slash_command(name="clock_rem", description="Removes the selected saved clock")
    async def remove_clock(self, ctx, clock_name: str):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if clock_name in clock_dic:
            del clock_dic[clock_name]
            save_clocks(user_id, clock_dic)
            await ctx.respond(content="The clock has been deleted!\n")
        else:
            await ctx.respond("Clock does not exist: " + clock_name)

    @commands.slash_command(name="clock_show", description="Prints a saved clock, with picture if possible")
    async def show_clock(self, ctx, clock_name):
        user_id = str(ctx.author.id)
        clock_dic = load_clocks(user_id)
        if clock_name in clock_dic:
            await print_clock(ctx, clock_dic[clock_name])
        else:
            await ctx.respond("This clock does not exist")

    @commands.slash_command(name="clock_all", description="Prints out all saved clocks")
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

    @commands.slash_command(name="clock_tick", description="Ticks the selected clock by a selected amount. Default: 1 tick")
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
