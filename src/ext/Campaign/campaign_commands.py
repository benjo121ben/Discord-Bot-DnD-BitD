from discord.ext import commands
from discord.ext.commands import Context
from .CommandFunctions import *


def get_char_name_if_none(char_name: str, ctx: Context):
    if char_name is None:
        for char in charDic.values():
            if char.player == str(ctx.author.id):
                return char.name
        raise CommandException("No character was assigned to this ID. Either claim a character or add the name as a parameter")
    return char_name


@commands.command(name="addChar")
async def add_c(ctx, char_name: str, max_health: int, user_name: str = ""):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(add_char(user_name, char_name, max_health))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="cause")
async def cause(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(cause_damage(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="take")
async def take(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(take_damage(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="takeR")
async def takeR(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(take_damage_res(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="inc")
async def increase(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(increase_health(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="heal")
async def heal_single(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(heal(char_name, amount))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="healm")
async def full_h(ctx, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.send(heal_max(char_name))
    except CommandException as err:
        await ctx.send(err)


@commands.command(name="claim")
async def claim(ctx: Context, char_name: str, user_id: str = None):
    if user_id is None:
        user_id = str(ctx.author.id)
    try:
        for char in charDic.values():
            if char.player == user_id:
                raise CommandException("this user already has character " + char.name + " assigned")
        check_char_name(char_name)
        if charDic[char_name].player != "" and charDic[char_name].player != str(ctx.author.id):
            raise CommandException("You are not authorized to assign this character. It has already been claimed by a user.")
        charDic[char_name].player = user_id
        save()
        await ctx.send(char_name + " assigned to " + user_id)
    except CommandException as err:
        await ctx.send(str(err))


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
    bot.add_command(takeR)
    bot.add_command(heal_single)
    bot.add_command(full_h)
    bot.add_command(increase)
    bot.add_command(logger)
    bot.add_command(claim)

    print("campaign extension loaded\n")
