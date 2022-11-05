import os
from os.path import exists

import discord.errors as d_errors
from discord import slash_command
from discord.ext import commands
from discord.ext.bridge import BridgeExtContext, Bot
from os.path import getmtime

from . import Undo, CommandFunctions as cfuncs, packg_variables as cmp_vars, campaign_helper as cmp_hlp, campaign_exceptions as cmp_except


class CampaignCog(commands.Cog):
    @slash_command(name="crit", description="Character has rollet a nat20")
    async def crit(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            cmp_hlp.check_char_name(char_name, raise_error=True)
            crits = cmp_vars.charDic[char_name].crits
            Undo.queue_basic_action(char_name, "crits", crits, crits + 1)
            cmp_vars.charDic[char_name].rolled_crit()
            cmp_hlp.save()
            await ctx.respond(f"Crit of {char_name} increased by 1")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="dodged", description="Character dodged an attack")
    async def dodged(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            cmp_hlp.check_char_name(char_name, raise_error=True)
            dodged = cmp_vars.charDic[char_name].dodged
            Undo.queue_basic_action(char_name, "dodged", dodged, dodged + 1)
            cmp_vars.charDic[char_name].dodge()
            cmp_hlp.save()
            await ctx.respond(f"Character {char_name}, dodged an attack")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: BridgeExtContext, amount: int, kills: int = 0, char_name: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            await ctx.respond(cfuncs.cause_damage(char_name, amount, kills))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="take", description="Character takes damage, reducing their health and maybe causing them to faint")
    async def take(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            await ctx.respond(cfuncs.take_damage(char_name, amount, False))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="tank", description="Character tanks damage, not reducing their health")
    async def tank(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            cmp_hlp.check_char_name(char_name, raise_error=True)
            undo_action = Undo.MultipleBaseAction(cmp_vars.charDic[char_name], ["damage_taken"])
            cmp_vars.charDic[char_name].tank(amount)
            cmp_hlp.save()
            undo_action.update(cmp_vars.charDic[char_name])
            Undo.queue_undo_action(undo_action)
            await ctx.respond(f"{char_name} tanks {amount} damage")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="taker", description="Character takes reduced damage, reducing health and maybe causing a faint")
    async def take_reduced(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            await ctx.respond(cfuncs.take_damage(char_name, amount, True))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="set_max",
        description="Sets Characters maximum health to the given amount, adjusting the current health by the difference"
    )
    async def set_max(self, ctx: BridgeExtContext, new_max_health: int, char_name: str = None):
        new_max_health = abs(new_max_health)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            await ctx.respond(cfuncs.set_max_health(char_name, new_max_health))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="heal",
        description="Heals a character. If char_name is set to \"all\" then this will apply to all Characters"
    )
    async def heal_single(self, ctx: BridgeExtContext, amount: int, char_name: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            await ctx.respond(cfuncs.heal(char_name, amount))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="healm",
        description="Heals a character to his max hp. If char_name is set to \"all\" then this will apply to all Characters"
    )
    async def full_h(self, ctx: BridgeExtContext, char_name: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_name = cmp_hlp.get_char_name_if_none(ctx, char_name)
            await ctx.respond(cfuncs.heal_max(char_name))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="log", description="Outputs all current Character information")
    async def logger(self, ctx: BridgeExtContext, adv = False):
        try:
            await ctx.respond(cfuncs.log(adv))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    # management commands

    @slash_command(
        name="add_char",
        description="Add Character to save file. If user_id is provided, it tries to claim the character for that user"
    )
    async def add_c(self, ctx: BridgeExtContext, char_name: str, max_health: int, user_id: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            await ctx.respond(cfuncs.add_char(char_name, max_health))
            if user_id is not None:
                await self.claim(ctx, char_name, user_id)
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="rename_char",
        description="Rename a character on the current save file."
    )
    async def rename_player_character(self, ctx: BridgeExtContext, char_name_old: str, char_name_new: str):
        try:
            cfuncs.rename_char(char_name_old, char_name_new)
            Undo.queue_undo_action(Undo.RenameCharUndoAction(char_name_old, char_name_new))
            await ctx.respond(f"Character {char_name_old} has been renamed to {char_name_new}")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="file",
        description="Load an existing campaign save file or create a new one"
    )
    async def file(self, ctx: BridgeExtContext, file_name: str):
        old_file_name = cmp_hlp.get_save_file_name_no_suff()
        ret_str = cmp_hlp.load(file_name)
        Undo.queue_undo_action(Undo.FileChangeUndoAction(old_file_name, cmp_hlp.get_save_file_name_no_suff()))
        await ctx.respond(ret_str)

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: BridgeExtContext, char_name: str, user_id: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            if user_id is None:
                user_id = ctx.author.id
            if cmp_hlp.check_if_user_has_char(user_id):
                raise cmp_except.CommandException(f"this user already has character {cmp_hlp.get_char_name_by_id(user_id)} assigned")
            cmp_hlp.check_char_name(char_name, raise_error=True)

            current_player = cmp_vars.charDic[char_name].player

            if not cmp_hlp.check_file_admin(ctx) and current_player != "" and int(current_player) != ctx.author.id:
                raise cmp_except.CommandException("You are not authorized to assign this character. It has already been claimed by a user.")

            user = ""
            try:
                user = await cmp_hlp.get_bot().fetch_user(user_id)
            except d_errors.NotFound as err:
                print(str(err))
                await ctx.respond("This user does not exist")
                return

            cmp_vars.charDic[char_name].player = str(user_id)
            Undo.queue_basic_action(char_name, "player", current_player, str(user_id))
            cmp_hlp.save()
            await ctx.respond(f"{char_name} assigned to {user.name}")
        except cmp_except.CommandException as err:
            await ctx.respond(str(err))

    @slash_command(name="unclaim", description="Unclaim an assigned Character")
    async def unclaim(self, ctx: BridgeExtContext, user_id: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            if user_id is not None and not cmp_hlp.check_file_admin(ctx):
                raise cmp_except.CommandException("You are not authorized to use this command on other people's characters")
            if user_id is None:
                user_id = ctx.author.id
            if not cmp_hlp.check_if_user_has_char(user_id):
                raise cmp_except.CommandException("this user has no character assigned")
            char_name = cmp_hlp.get_char_name_by_id(user_id)
            Undo.queue_basic_action(char_name, "player", str(user_id), "")
            cmp_vars.charDic[char_name].player = ""
            cmp_hlp.save()
            await ctx.respond(f"Character {char_name} unassigned")
        except cmp_except.CommandException as err:
            await ctx.respond(str(err))

    @slash_command(name="session", description="increase session")
    async def session(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            if not cmp_hlp.check_file_admin(ctx):
                raise cmp_except.CommandException("You are not authorized to use this command")
            cmp_vars.imported_dic[cmp_hlp.session_tag] += 1
            cmp_hlp.save()
            await ctx.respond("finished session, increased by one")
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="cache", description="Admin command: caches the last save file into the provided server chat")
    async def cache(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            if not cmp_hlp.check_bot_admin(ctx):
                raise cmp_except.CommandException("You are not authorized to use this command")

            chat_id = cmp_vars.cache_folder
            if chat_id is None:
                raise cmp_except.CommandException("No cloudsavechannel id assigned")

            await cmp_hlp.get_bot().get_channel(chat_id).send("cache", file=cmp_hlp.get_file())
            await ctx.respond("cached")
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="get_cache", description="try to download latestsavefrom cache server chat")
    async def get_cache(self, ctx: BridgeExtContext):
        try:
            if not cmp_hlp.check_bot_admin(ctx):
                raise cmp_except.CommandException("You are not authorized to use this command")

            chat_id = cmp_vars.cache_folder
            if chat_id is None:
                raise cmp_except.CommandException("No cloudsavechannel id assigned")

            message = await cmp_hlp.get_bot().get_channel(chat_id).history(limit=1).next()
            filename = message.attachments[0].filename
            cache_save_path = cmp_hlp.cache_location_relative_to_base + '/' + filename
            local_save_path = cmp_hlp.saves_location_relative_to_base + '/' + filename

            await message.attachments[0].save(fp=cache_save_path)
            if not exists(local_save_path):
                os.rename(cache_save_path, local_save_path)
                await ctx.respond(f"No local version found.save{filename} has been imported.")
                return

            if cmp_hlp.compare_savefile_date(local_save_path, cache_save_path) == -1:
                os.remove(local_save_path)
                os.rename(cache_save_path, local_save_path)
                await ctx.respond("replaced")
            else:
                os.remove(cache_save_path)
                await ctx.respond("already up to date")
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="download", description="Downloads the selectedsavefile")
    async def download(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            await ctx.respond("save file:", file=cmp_hlp.get_file())
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="undo", description="Undo your mistakes")
    async def undo_comm(self, ctx: BridgeExtContext, amount: int = 1):
        try:
            if amount > 10:
                amount = 10
            cmp_hlp.check_file_loaded(raise_error=True)
            ret_val = ""
            for _ in range(amount):
                ret_val += Undo.undo() + "\n"
                if not cmp_hlp.get_save_file_name_no_suff() == "":
                    cmp_hlp.save()
            await ctx.respond(ret_val)
        except Exception as err:
            await ctx.respond(str(err))

    @slash_command(name="redo", description="Redo your undone non-mistakes")
    async def redo_comm(self, ctx: BridgeExtContext, amount: int = 1):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            ret_val = ""
            for _ in range(amount):
                ret_val += Undo.redo() + "\n"
                if not cmp_hlp.get_save_file_name_no_suff() == "":
                    cmp_hlp.save()
            await ctx.respond(ret_val)
        except Exception as err:
            await ctx.respond(str(err))

    @commands.command(name="save")
    async def save_command(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            cmp_hlp.save()
            await ctx.respond("saved")
        except Exception as err:
            await ctx.respond(str(err))


def setup(bot: Bot):
    cmp_hlp.check_base_setup()
    bot.add_cog(CampaignCog())

    print("campaign extension loaded\n")
