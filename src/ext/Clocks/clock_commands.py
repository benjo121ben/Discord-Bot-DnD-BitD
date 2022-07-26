from discord.ext import commands
from .clocks import *


async def print_clock(ctx, clock):
    try:
        await ctx.send("**" + clock.name + "**", file=clock.get_embed_info()[1])
    except NoClockImageException as err:
        await ctx.send("Clocks of this size have missing output images\n**"
                       + str(clock) + "**")
        print(
            "clock of size ",
            str(clock.size),
            "was printed without image, make sure images are included for all clocks needed."
        )


@commands.command(name="addClock")
async def add_clock(ctx, clock_name: str, clock_size: int, clock_ticks: int = 0):
    if clock_name in clocks_save_dic:
        await ctx.send( content="This clock already exists!\n")
        await print_clock(ctx, clocks_save_dic[clock_name])
    else:
        clocks_save_dic[clock_name] = Clock(clock_name, clock_size, clock_ticks)
        save_clocks()
        await ctx.send("Clock created")
        await print_clock(ctx, clocks_save_dic[clock_name])


@commands.command(name="remClock")
async def remove_clock(ctx, clock_name: str):
    if clock_name in clocks_save_dic:
        del clocks_save_dic[clock_name]
        save_clocks()
        await ctx.send( content="The clock has been deleted!\n")
    else:
        await ctx.send("Clock does not exist: " + clock_name)


@commands.command(name="show")
async def show_clocks(ctx, *args):
    await ctx.send("printing clocks")

    if len(args) > 0:
        for name in args:
            if clocks_save_dic.__contains__(name):
                await print_clock(ctx, clocks_save_dic[name])
    else:
        for _, clock in clocks_save_dic.items():
            await print_clock(ctx, clock)


@commands.command(name="tick")
async def tick_clock(ctx, clock_name: str, ticks: int = 1):
    clock = clocks_save_dic.get(clock_name)
    if clock:
        clock.tick(ticks)
        save_clocks()
        await print_clock(ctx, clock)


def setup(bot: commands.bot.Bot):
    # Every extension should have this function
    load_clocks()
    bot.add_command(add_clock)
    bot.add_command(show_clocks)
    bot.add_command(tick_clock)
    bot.add_command(remove_clock)

    print("clock extension loaded")
    print()
