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
    async def crit(self, ctx: BridgeExtContext, char_tag: str = None):
        try:
            print(cmp_vars.charDic)
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            cmp_hlp.check_char_tag(char_tag, raise_error=True)
            crits = cmp_vars.charDic[char_tag].crits
            Undo.queue_basic_action(char_tag, "crits", crits, crits + 1)
            cmp_vars.charDic[char_tag].rolled_crit()
            cmp_hlp.save()
            await ctx.respond(f"Crit of {char_tag} increased by 1")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="dodged", description="Character dodged an attack")
    async def dodged(self, ctx: BridgeExtContext, char_tag: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            cmp_hlp.check_char_tag(char_tag, raise_error=True)
            dodged = cmp_vars.charDic[char_tag].dodged
            Undo.queue_basic_action(char_tag, "dodged", dodged, dodged + 1)
            cmp_vars.charDic[char_tag].dodge()
            cmp_hlp.save()
            await ctx.respond(f"Character {char_tag}, dodged an attack")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: BridgeExtContext, amount: int, kills: int = 0, char_tag: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.cause_damage(char_tag, amount, kills))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="take", description="Character takes damage, reducing their health and maybe causing them to faint")
    async def take(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.take_damage(char_tag, amount, False))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="tank", description="Character tanks damage, not reducing their health")
    async def tank(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            cmp_hlp.check_char_tag(char_tag, raise_error=True)
            undo_action = Undo.MultipleBaseAction(cmp_vars.charDic[char_tag], ["damage_taken"])
            cmp_vars.charDic[char_tag].tank(amount)
            cmp_hlp.save()
            undo_action.update(cmp_vars.charDic[char_tag])
            Undo.queue_undo_action(undo_action)
            await ctx.respond(f"{char_tag} tanks {amount} damage")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(name="taker", description="Character takes reduced damage, reducing health and maybe causing a faint")
    async def take_reduced(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.take_damage(char_tag, amount, True))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="set_max",
        description="Sets Characters maximum health to the given amount, adjusting the current health by the difference"
    )
    async def set_max(self, ctx: BridgeExtContext, new_max_health: int, char_tag: str = None):
        new_max_health = abs(new_max_health)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.set_max_health(char_tag, new_max_health))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="heal",
        description="Heals a character. If char_tag is set to \"all\" then this will apply to all Characters"
    )
    async def heal_single(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.heal(char_tag, amount))
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="healm",
        description="Heals a character to his max hp. If char_tag is set to \"all\" then this will apply to all Characters"
    )
    async def full_h(self, ctx: BridgeExtContext, char_tag: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.heal_max(char_tag))
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
    async def add_c(self, ctx: BridgeExtContext, char_tag: str, char_name: str, max_health: int, user_id: str = None):
        try:
            if char_tag == "all":
                await ctx.respond("You are not allowed to call your character all, due to special commands using it a keyword. Please call them something else")
                return
            cmp_hlp.check_file_loaded(raise_error=True)
            await ctx.respond(cfuncs.add_char(char_tag, char_name, max_health))
            if user_id is not None:
                await self.claim(ctx, char_tag, user_id)
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="retag_char",
        description="Retag a character on the current save file."
    )
    async def retag_player_character(self, ctx: BridgeExtContext, char_tag_old: str, char_tag_new: str):
        try:
            cfuncs.rename_char_tag(char_tag_old, char_tag_new)
            Undo.queue_undo_action(Undo.ReTagCharUndoAction(char_tag_old, char_tag_new))
            await ctx.respond(f"Character {char_tag_old} has been renamed to {char_tag_new}")
        except cmp_except.CommandException as err:
            await ctx.respond(err)

    @slash_command(
        name="file",
        description="Load an existing campaign save file or create a new one"
    )
    async def file(self, ctx: BridgeExtContext, file_name: str):
        old_file_name = cmp_hlp.get_current_save_file_name_no_suff()
        ret_str = cmp_hlp.load(file_name)
        Undo.queue_undo_action(Undo.FileChangeUndoAction(old_file_name, cmp_hlp.get_current_save_file_name_no_suff()))
        await ctx.respond(ret_str)

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: BridgeExtContext, char_tag: str, user_id: str = None):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            if user_id is None:
                user_id = ctx.author.id
            if cmp_hlp.check_if_user_has_char(user_id):
                raise cmp_except.CommandException(f"this user already has character {cmp_hlp.get_char_tag_by_id(user_id)} assigned")
            cmp_hlp.check_char_tag(char_tag, raise_error=True)

            current_player = cmp_vars.charDic[char_tag].player

            if not cmp_hlp.check_file_admin(ctx) and current_player != "" and int(current_player) != ctx.author.id:
                raise cmp_except.CommandException("You are not authorized to assign this character. It has already been claimed by a user.")

            user = ""
            try:
                user = await cmp_hlp.get_bot().fetch_user(user_id)
            except d_errors.NotFound as err:
                print(str(err))
                await ctx.respond("This user does not exist")
                return

            cmp_vars.charDic[char_tag].player = str(user_id)
            Undo.queue_basic_action(char_tag, "player", current_player, str(user_id))
            cmp_hlp.save()
            await ctx.respond(f"{char_tag} assigned to {user.name}")
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
            char_tag = cmp_hlp.get_char_tag_by_id(user_id)
            Undo.queue_basic_action(char_tag, "player", str(user_id), "")
            cmp_vars.charDic[char_tag].player = ""
            cmp_hlp.save()
            await ctx.respond(f"Character {char_tag} unassigned")
        except cmp_except.CommandException as err:
            await ctx.respond(str(err))

    @slash_command(name="session", description="increase session")
    async def session(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_file_loaded(raise_error=True)
            if not cmp_hlp.check_file_admin(ctx):
                raise cmp_except.CommandException("You are not authorized to use this command")
            if cmp_hlp.check_bot_admin(ctx):
                await self.cache(ctx)
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
            message = f"cache-{cmp_hlp.get_current_save_file_name_no_suff()}-session {cmp_vars.imported_dic['session']}"
            await cmp_hlp.get_bot().get_channel(chat_id).send(message, file=cmp_hlp.get_current_savefile_as_discord_file())
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
            cache_save_path = cmp_hlp.get_cache_folder_filepath() + f'{os.sep}' + filename
            local_save_path = cmp_hlp.get_cache_folder_filepath() + f'{os.sep}' + filename

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
            await ctx.respond("save file:", file=cmp_hlp.get_current_savefile_as_discord_file())
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
                if not cmp_hlp.get_current_save_file_name_no_suff() == "":
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
                if not cmp_hlp.get_current_save_file_name_no_suff() == "":
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
