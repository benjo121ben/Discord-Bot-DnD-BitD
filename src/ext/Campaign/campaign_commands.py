from discord.ext import commands
from .CommandFunctions import *


@commands.command(name="addChar")
async def add_c(ctx, user_name: str, char_name: str, max_health: int):
    try:
        await ctx.send(add_char(user_name,char_name,max_health))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="cause")
async def cause(ctx, char_name: str, amount: int):
    try:
        await ctx.send(cause_damage(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="take")
async def take(ctx, char_name: str, amount: int):
    try:
        await ctx.send(take_damage(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="inc")
async def increase(ctx, char_name: str, amount: int):
    try:
        await ctx.send(increase_health(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="heal")
async def heal_single(ctx, char_name: str, amount: int):
    try:
        await ctx.send(heal(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="healm")
async def full_h(ctx, char_name: str):
    try:
        await ctx.send(heal_max(char_name))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="log")
async def logger(ctx):
    try:
        await ctx.send(log())
    except CommandException as err:
        await ctx.send(err)


def setup(bot: commands.bot.Bot):
    bot.add_command(add_c)
    bot.add_command(cause)
    bot.add_command(take)
    bot.add_command(heal_single)
    bot.add_command(full_h)
    bot.add_command(increase)
    bot.add_command(logger)

    print("campaign extension loaded\n")
