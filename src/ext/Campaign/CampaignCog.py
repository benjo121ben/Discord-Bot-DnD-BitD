import os

import discord.errors
from discord import slash_command
from discord.ext import commands
from discord.ext import bridge
from discord.ext.bridge import BridgeExtContext
import src.ext.Campaign.Undo as Undo
from os.path import getmtime

from .CommandFunctions import *
from src import GlobalVariables, command_helper_functions as hlp_f
from .campaign_helper import check_file_loaded, rename_char, get_save_file_name_no_suff, check_if_user_has_char


class CampaignCog(commands.Cog):
    @slash_command(name="crit", description="Character has rollet a nat20")
    async def crit(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            check_char_name(char_name, raise_error=True)
            crits = charDic[char_name].crits
            Undo.queue_basic_action(char_name, "crits", crits, crits + 1)
            charDic[char_name].rolled_crit()
            save()
            await ctx.respond(f"Crit of {char_name} increased by 1")
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="dodged", description="Character dodged an attack")
    async def dodged(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            check_char_name(char_name, raise_error=True)
            dodged = charDic[char_name].dodged
            Undo.queue_basic_action(char_name, "dodged", dodged, dodged + 1)
            charDic[char_name].dodge()
            save()
            await ctx.respond(f"Character {char_name}, dodged an attack")
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: BridgeExtContext, amount: int, kills: int = 0, char_name: str = None):
        amount = abs(amount)
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(cause_damage(char_name, amount, kills))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="take", description="Character takes damage, reducing their health and maybe causing them to faint")
    async def take(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(take_damage(char_name, amount, False))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="tank", description="Character tanks damage, not reducing their health")
    async def tank(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            check_char_name(char_name, raise_error=True)
            undo_action = Undo.MultipleBaseAction(charDic[char_name], ["damage_taken"])
            charDic[char_name].tank(amount)
            undo_action.update(charDic[char_name])
            Undo.queue_undo_action(undo_action)
            await ctx.respond(f"{char_name} tanks {amount} damage")
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(name="taker", description="Character takes reduced damage, reducing health and maybe causing a faint")
    async def take_reduced(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(take_damage(char_name, amount, True))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="set_max",
        description="Sets Characters maximum health to the given amount, adjusting the current health by the difference"
    )
    async def set_max(self, ctx: BridgeExtContext, new_max_health: int, char_name: str = None):
        new_max_health = abs(new_max_health)
        try:
            check_file_loaded(raise_error=True)
            char_name = get_char_name_if_none(char_name, ctx)
            await ctx.respond(set_max_health(char_name, new_max_health))
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="heal",
        description="Heals a character. If char_name is set to \"all\" then this will apply to all Characters"
    )
    async def heal_single(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
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
    async def logger(self, ctx: BridgeExtContext, adv = False):
        try:
            await ctx.respond(log(adv))
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
    async def rename_player_character(self, ctx: BridgeExtContext, char_name_old: str, char_name_new: str):
        try:
            rename_char(char_name_old, char_name_new)
            Undo.queue_undo_action(Undo.RenameCharUndoAction(char_name_old, char_name_new))
            await ctx.respond(f"Character {char_name_old} has been renamed to {char_name_new}")
        except CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="file",
        description="Load an existing campaign save file or create a new one"
    )
    async def file(self, ctx: BridgeExtContext, file_name: str):
        old_file_name = get_save_file_name_no_suff()
        ret_str = load(file_name)
        Undo.queue_undo_action(Undo.FileChangeUndoAction(old_file_name, get_save_file_name_no_suff()))
        await ctx.respond(ret_str)

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: BridgeExtContext, char_name: str, user_id: str = None):
        try:
            check_file_loaded(raise_error=True)
            if user_id is None:
                user_id = ctx.author.id
            if check_if_user_has_char(user_id):
                raise CommandException(f"this user already has character {get_char_name_if_none(None,ctx)} assigned")
            check_char_name(char_name, raise_error=True)

            current_player = charDic[char_name].player

            if not hlp_f.check_admin(ctx) and current_player != "" and int(current_player) != ctx.author.id:
                raise CommandException("You are not authorized to assign this character. It has already been claimed by a user.")

            user = ""
            try:
                user = await GlobalVariables.bot.fetch_user(user_id)
            except discord.errors.NotFound as err:
                print(str(err))
                await ctx.respond("This user does not exist")
                return

            charDic[char_name].player = str(user_id)
            Undo.queue_basic_action(char_name, "player", current_player, str(user_id))
            save()
            await ctx.respond(f"{char_name} assigned to {user.name}")
        except CommandException as err:
            await ctx.respond(str(err))

    @slash_command(name="unclaim", description="Unclaim an assigned Character")
    async def unclaim(self, ctx: BridgeExtContext, user_id: str = None):
        try:
            check_file_loaded(raise_error=True)
            if user_id is not None and not hlp_f.check_admin(ctx):
                raise CommandException("You are not authorized to use this command on other peoples characters")
            if user_id is None:
                user_id = ctx.author.id
            if not check_if_user_has_char(user_id):
                raise CommandException("this user has no character assigned")
            char_name = get_char_name_if_none(None, ctx)
            Undo.queue_basic_action(char_name, "player", str(user_id), "")
            charDic[char_name].player = ""
            save()
            await ctx.respond(f"Character {char_name} unassigned")
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
                raise CommandException("No cloud save channel id assigned")

            await GlobalVariables.bot.get_channel(chat_id).send("cache", file=get_file())
            await ctx.respond("cached")
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="get_cache", description="try to download latest save from cache server chat")
    async def get_cache(self, ctx: BridgeExtContext):
        try:
            if not hlp_f.check_admin(ctx):
                raise CommandException("You are not authorized to use this command")

            chat_id = GlobalVariables.cache_folder
            if chat_id is None:
                raise CommandException("No cloud save channel id assigned")

            message = await GlobalVariables.bot.get_channel(chat_id).history(limit=1).next()
            filename = message.attachments[0].filename
            await message.attachments[0].save(fp=cache_location_relative_to_base + '/' + filename)

            if not exists(saves_location_relative_to_base + '/' + filename):
                os.rename(cache_location_relative_to_base + '/' + filename, saves_location_relative_to_base + '/' + filename)
                await ctx.respond(f"No local version found. Savefile {filename} has been imported.")
                return

            cache_time = getmtime(cache_location_relative_to_base + '/' + filename)
            local_time = getmtime(saves_location_relative_to_base + '/' + filename)
            print(local_time)
            print(cache_time)
            if local_time < cache_time:
                os.remove(saves_location_relative_to_base + '/' + filename)
                os.rename(cache_location_relative_to_base + '/' + filename, saves_location_relative_to_base + '/' + filename)
                await ctx.respond("replaced")
            else:
                os.remove(cache_location_relative_to_base + '/' + filename)
                await ctx.respond("already up to date")
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="download", description="Downloads the selected save file")
    async def download(self, ctx: BridgeExtContext):
        try:
            check_file_loaded(raise_error=True)
            await ctx.respond("save file:", file=get_file())
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="undo", description="Undo your mistakes")
    async def undo_comm(self, ctx: BridgeExtContext, amount: int = 1):
        try:
            if amount > 10:
                amount = 10
            check_file_loaded(raise_error=True)
            ret_val = ""
            for _ in range(amount):
                ret_val += Undo.undo() + "\n"
                if not get_save_file_name_no_suff() == "":
                    save()
            await ctx.respond(ret_val)
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="redo", description="Redo your undone non-mistakes")
    async def redo_comm(self, ctx: BridgeExtContext, amount: int = 1):
        try:
            check_file_loaded(raise_error=True)
            ret_val = ""
            for _ in range(amount):
                ret_val += Undo.redo() + "\n"
                if not get_save_file_name_no_suff() == "":
                    save()
            await ctx.respond(ret_val)
        except Exception as err:
            await ctx.respond(str(err))

    @commands.command(name="save")
    async def save(self, ctx: BridgeExtContext):
        try:
            check_file_loaded(raise_error=True)
            save()
            await ctx.respond("saved")
        except Exception as err:
            await ctx.respond(str(err))

def setup(bot: bridge.Bot):
    check_base_save_folder_setup()
    bot.add_cog(CampaignCog())

    print("campaign extension loaded\n")
