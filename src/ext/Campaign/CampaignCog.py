import discord.errors
from discord import slash_command
from discord.ext import commands
from discord.ext import bridge
from discord.ext.bridge import BridgeExtContext

from .CommandFunctions import *
from src import GlobalVariables, command_helper_functions as hlp_f
from .campaign_helper import check_file_loaded


class CampaignCog(commands.Cog):
    @slash_command(name="crit", description="Character has rollet a nat20")
    async def crit(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            charDic[char_name].rolled_crit()
            await ctx.respond(f"Crit of {char_name} increased by 1")
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: BridgeExtContext, amount: int, kills: int = 0, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(cause_damage(char_name, amount, kills))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="take", description="Character takes damage")
    async def take(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(take_damage(char_name, amount))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="taker", description="Character takes reduced damage")
    async def take_reduced(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(take_damage_res(char_name, amount))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="set_max",
        description="Sets Characters maximum health to the given amount, adjusting the current health by the difference"
    )
    async def set_max(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(set_max_health(char_name, amount))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="heal",
        description="Heals a character. If char_name is set to \"all\" then this will apply to all Characters"
    )
    async def heal_single(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(heal(char_name, amount))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="healm",
        description="Heals a character to his max hp. If char_name is set to \"all\" then this will apply to all Characters"
    )
    async def full_h(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(heal_max(char_name))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="log", description="Outputs all current Character information")
    async def logger(self, ctx: BridgeExtContext):
        try:
            await ctx.respond(log())
        except CommandException as err:
            await ctx.respond(err)

    # management commands

    @slash_command(
        name="add_char",
        description="Add Character to saveFile. If user_id is provided, it tries to claim the character for that user"
    )
    async def add_c(self, ctx: BridgeExtContext, char_name: str, max_health: int, user_id: str = None):
        try:
            check_file_loaded(raise_error=True)
            await ctx.respond(add_char(char_name, max_health))
            if user_id is not None:
                await self.claim(ctx, char_name, user_id)
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="rename_char",
        description="Rename a character on the current save file."
    )
    async def rename_char(self, ctx: BridgeExtContext, char_name_old: str, char_name_new: str):
        try:
            check_file_loaded(raise_error=True)
            check_char_name(char_name_old, raise_error=True)
            if check_char_name(char_name_new):
                raise CommandException("A Character of this name already exists")

            charDic[char_name_new] = charDic[char_name_old]
            charDic[char_name_new].name = char_name_new
            del charDic[char_name_old]
            save()
            await ctx.respond(f"Character {char_name_old} has been renamed to {char_name_new}")
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="file",
        description="Load an existing campaign save file or create a new one"
    )
    async def file(self, ctx: BridgeExtContext, file_name):
        await ctx.respond(load(file_name))

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: BridgeExtContext, char_name: str, user_id: str = None):
        try:
            check_file_loaded(raise_error=True)
            if user_id is None:
                user_id = ctx.author.id
            for char in charDic.values():
                if char.player == user_id:
                    raise CommandException("this user already has character " + char.name + " assigned")
            check_char_name(char_name, raise_error=True)

            if charDic[char_name].player != "" and int(charDic[char_name].player) != ctx.author.id:
                raise CommandException("You are not authorized to assign this character. It has already been claimed by a user.")
            try:
                user = await GlobalVariables.bot.fetch_user(user_id)
                charDic[char_name].player = str(user_id)
                save()
                await ctx.respond(f"{char_name} assigned to {user.name}")
            except discord.errors.NotFound as err:
                print(str(err))
                await ctx.respond("This user does not exist")
        except CommandException as err:
            await ctx.respond(str(err))

    @slash_command(name="unclaim", description="Unclaim your own assigned Character")
    async def unclaim(self, ctx: BridgeExtContext, user_id: str = None):
        try:
            check_file_loaded(raise_error=True)
            if user_id is not None and not hlp_f.check_admin(ctx):
                raise CommandException("You are not authorized to use this command")
            if user_id is None:
                user_id = ctx.author.id
            for char in charDic.values():
                if char.player == user_id:
                    charDic[char.name].player = ""
                    save()
                    await ctx.respond("Character " + char.name + " unassigned")
                    return
            raise CommandException("this user has no character assigned")
        except CommandException as err:
            await ctx.respond(str(err))

    @slash_command(name="cache", description="Admin command: caches the last save file into the provided server chat")
    async def cache(self, ctx: BridgeExtContext):
        try:
            check_file_loaded(raise_error=True)
            if not hlp_f.check_admin(ctx):
                raise CommandException("You are not authorized to use this command")

            chat_id = GlobalVariables.cache_folder
            if chat_id is None:
                raise CommandException("No cloud save channel id assigned or provided")

            await GlobalVariables.bot.get_channel(chat_id).send("cache", file=get_file())
            await ctx.respond("cached")
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="download", description="Downloads the selected save file")
    async def download(self, ctx: BridgeExtContext):
        try:
            check_file_loaded(raise_error=True)
            await ctx.respond("save file:", file=get_file())
        except Exception as err:
            await ctx.respond(str(err))


def setup(bot: bridge.Bot):
    bot.add_cog(CampaignCog())

    print("campaign extension loaded\n")
