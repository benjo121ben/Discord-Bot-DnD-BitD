import discord.errors
from discord import slash_command
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext import bridge

from .CommandFunctions import *
from src import GlobalVariables, command_helper_functions as hlp_f


def get_char_name_if_none(char_name: str, ctx: Context):
    if char_name is not None:
        return char_name

    for char in charDic.values():
        if char.player == str(ctx.author.id):
            return char.name
    raise CommandException("No character was assigned to this ID. Either claim a character or add the name as a parameter")


@slash_command(name="cause", description="Character causes damage to enemy")
async def cause(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(cause_damage(char_name, amount))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="take", description="Character takes damage")
async def take(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(take_damage(char_name, amount))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="taker", description="Character takes reduced damage")
async def takeR(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(take_damage_res(char_name, amount))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="set_max", description="Sets Characters maximum health to the given amount, adjusting the current health by the difference")
async def set_max(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(set_max_health(char_name, amount))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="heal")
async def heal_single(ctx, amount: int, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(heal(char_name, amount))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="healm")
async def full_h(ctx, char_name: str = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(heal_max(char_name))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="log")
async def logger(ctx):
    try:
        await ctx.respond(log())
    except CommandException as err:
        await ctx.respond(err)


# management commands

@slash_command(name="add_char")
async def add_c(ctx, char_name: str, max_health: int, user_name: int = None):
    try:
        char_name = get_char_name_if_none(char_name, ctx)
        await ctx.respond(add_char(user_name, char_name, max_health))
    except CommandException as err:
        await ctx.respond(err)


@slash_command(name="claim")
async def claim(ctx: Context, char_name: str, user_id: int = None):
    try:
        if user_id is None:
            user_id = ctx.author.id
        for char in charDic.values():
            if char.player == user_id:
                raise CommandException("this user already has character " + char.name + " assigned")
        check_char_name(char_name)
        if charDic[char_name].player != "" and int(charDic[char_name].player) != ctx.author.id:
            raise CommandException("You are not authorized to assign this character. It has already been claimed by a user.")
        try:
            user = await GlobalVariables.bot.fetch_user(user_id)
            charDic[char_name].player = user_id
            save()
            await ctx.respond(char_name + " assigned to " + user.name)
        except discord.errors.NotFound as err:
            print(str(err))
            await ctx.respond("This user does not exist")
    except CommandException as err:
        await ctx.respond(str(err))
        
        
@slash_command(name="unclaim")
async def unclaim(ctx: Context, user_id: int = None):
    if user_id is not None and not hlp_f.check_admin(ctx):
        raise CommandException("You are not authorized to use this command")
    if user_id is None:
        user_id = ctx.author.id
    try:
        for char in charDic.values():
            if char.player == user_id:
                charDic[char.name].player = ""
                save()
                await ctx.respond("Character " + char.name + " unassigned")
                return
        raise CommandException("this user has no character assigned")
    except CommandException as err:
        await ctx.respond(str(err))


@commands.command(name="cache")
async def cache(ctx: Context, chat_id: int = None):
    try:
        if not hlp_f.check_admin(ctx):
            raise CommandException("You are not authorized to use this command")

        if chat_id is None:
            chat_id = GlobalVariables.cache_folder
            if chat_id is None:
                raise CommandException("No cloud save channel id assigned or provided")

        await GlobalVariables.bot.get_channel(GlobalVariables.cache_folder).send("cache", file=get_file())
    except Exception as err:
        await ctx.send(str(err))


def setup(bot: bridge.Bot):
    get_setup_file_name()
    bot.add_application_command(add_c)
    bot.add_application_command(cause)
    bot.add_application_command(take)
    bot.add_application_command(takeR)
    bot.add_application_command(heal_single)
    bot.add_application_command(full_h)
    bot.add_application_command(set_max)
    bot.add_application_command(logger)
    bot.add_application_command(claim)
    bot.add_application_command(unclaim)
    bot.add_command(cache)

    print("campaign extension loaded\n")
