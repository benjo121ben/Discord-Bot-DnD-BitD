import os
from os.path import exists

import discord.errors as d_errors
from discord import slash_command
from discord.ext import commands
from discord.ext.bridge import BridgeExtContext, Bot
from .campaign_exceptions import CommandException as comm_except
from . import Undo, CommandFunctions as cfuncs, \
    packg_variables as cmp_vars, \
    campaign_helper as cmp_hlp, \
    save_file_management as save_manager


class CampaignCog(commands.Cog):
    @slash_command(name="crit", description="Character has rollet a nat20")
    async def crit(self, ctx: BridgeExtContext, char_tag: str = None):
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.crit(char_tag))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(name="dodged", description="Character dodged an attack")
    async def dodged(self, ctx: BridgeExtContext, char_tag: str = None):
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.dodged(char_tag))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: BridgeExtContext, amount: int, kills: int = 0, char_tag: str = None):
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.cause_damage(char_tag, amount, kills))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(name="take", description="Character takes damage, reducing their health and maybe causing them to faint")
    async def take(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.take_damage(char_tag, amount, False))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(name="tank", description="Character tanks damage, not reducing their health")
    async def tank(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.tank_damage(char_tag, amount))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(name="taker", description="Character takes reduced damage, reducing health and maybe causing a faint")
    async def take_reduced(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.take_damage(char_tag, amount, True))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(
        name="set_max",
        description="Sets Characters maximum health to the given amount, adjusting the current health by the difference"
    )
    async def set_max(self, ctx: BridgeExtContext, new_max_health: int, char_tag: str = None):
        new_max_health = abs(new_max_health)
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.set_max_health(char_tag, new_max_health))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(
        name="heal",
        description="Heals a character. If char_tag is set to \"all\" then this will apply to all Characters"
    )
    async def heal_single(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.heal(char_tag, amount))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(
        name="healm",
        description="Heals a character to his max hp. If char_tag is set to \"all\" then this will apply to all Characters"
    )
    async def full_h(self, ctx: BridgeExtContext, char_tag: str = None):
        try:
            char_tag = cmp_hlp.get_char_tag_if_none(ctx, char_tag)
            await ctx.respond(cfuncs.heal_max(char_tag))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(name="log", description="Outputs all current Character information")
    async def logger(self, ctx: BridgeExtContext, adv = False):
        try:
            await ctx.respond(cfuncs.log(adv))
        except comm_except as err:
            await ctx.respond(err)

    # management commands

    @slash_command(
        name="add_char",
        description="Add Character to save file. If user_id is provided, it tries to claim the character for that user"
    )
    async def add_c(self, ctx: BridgeExtContext, char_tag: str, char_name: str, max_health: int, user_id: str = None):
        try:
            await ctx.respond(cfuncs.add_char(char_tag, char_name, max_health))
            if user_id is not None:
                await self.claim(ctx, char_tag, user_id)
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(
        name="retag_char",
        description="Retag a character on the current save file."
    )
    async def retag_player_character(self, ctx: BridgeExtContext, char_tag_old: str, char_tag_new: str):
        try:
            await ctx.respond(cfuncs.retag_character(char_tag_old, char_tag_new))
        except comm_except as err:
            await ctx.respond(err)

    @slash_command(
        name="file",
        description="Load an existing campaign save file or create a new one"
    )
    async def file(self, ctx: BridgeExtContext, file_name: str):
        await ctx.respond(cfuncs.load_file(file_name))

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: BridgeExtContext, char_tag: str, user_id: str = None):
        try:
            if user_id is None:
                user_id = ctx.author.id
            cfuncs.claim_character(ctx.author.id, char_tag, user_id)
        except comm_except as err:
            await ctx.respond(str(err))
            return

        user = ""
        try:
            user = await cmp_hlp.get_bot().fetch_user(user_id)
        except d_errors.NotFound as err:
            print(str(err))
            await ctx.respond("A user with this ID could not be found by the bot.\n"
                              "Make sure the bot shares a server with the user that has this ID")
            Undo.undo()
            Undo.discard_undo_queue()
            return
        await ctx.respond(f"{char_tag} assigned to {user.name}")

    @slash_command(name="unclaim", description="Unclaim an assigned Character")
    async def unclaim(self, ctx: BridgeExtContext, user_id: str = None):
        try:
            if user_id is None:
                user_id = ctx.author.id
            await ctx.respond(cfuncs.unclaim_user(ctx.author.id, user_id))
        except comm_except as err:
            await ctx.respond(str(err))

    @slash_command(name="session", description="increase session")
    async def session(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_file_admin(ctx.author.id, raise_error=True)
            if cmp_hlp.check_bot_admin(ctx):
                await self.cache(ctx)
            await ctx.respond(cfuncs.session_increase())
        except comm_except as err:
            await ctx.respond(str(err))

    @slash_command(name="cache", description="Admin command: caches the last save file into the provided server chat")
    async def cache(self, ctx: BridgeExtContext):
        """
        Sends the current savefile into the discord chat with the ID assigned in the campaign environment file
        :param ctx: Discord context
        :raises NoSaveFileException if no savefile is present
        """
        try:
            save_manager.check_file_loaded(raise_error=True)
            cmp_hlp.check_bot_admin(ctx, raise_error=True)

            chat_id = cmp_vars.cache_folder
            if chat_id is None:
                raise comm_except("No cloudsavechannel id assigned")
            message = f"cache-{save_manager.get_current_save_file_name_no_suff()}-session {cmp_vars.imported_dic['session']}"
            current_file = save_manager.get_current_savefile_as_discord_file()
            await cmp_hlp.get_bot().get_channel(chat_id).send(message, file=current_file)
            await ctx.respond("cached")
        except comm_except as err:
            await ctx.respond(str(err))

    @slash_command(name="get_cache", description="try to download latestsavefrom cache server chat")
    async def get_cache(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_bot_admin(ctx, raise_error=True)
            chat_id = cmp_vars.cache_folder
            if chat_id is None:
                raise comm_except("No cloudsavechannel id assigned")

            message = await cmp_hlp.get_bot().get_channel(chat_id).history(limit=1).next()
            filename = message.attachments[0].filename
            cache_save_path = save_manager.get_cache_folder_filepath() + f'{os.sep}' + filename
            local_save_path = save_manager.get_cache_folder_filepath() + f'{os.sep}' + filename

            await message.attachments[0].save(fp=cache_save_path)
            if not exists(local_save_path):
                os.rename(cache_save_path, local_save_path)
                await ctx.respond(f"No local version found.save{filename} has been imported.")
                return

            if save_manager.compare_savefile_date(local_save_path, cache_save_path) == -1:
                os.remove(local_save_path)
                os.rename(cache_save_path, local_save_path)
                await ctx.respond("replaced")
            else:
                os.remove(cache_save_path)
                await ctx.respond("already up to date")
        except comm_except as err:
            await ctx.respond(str(err))

    @slash_command(name="download", description="Downloads the selectedsavefile")
    async def download(self, ctx: BridgeExtContext):
        try:
            save_manager.check_file_loaded(raise_error=True)
            await ctx.respond("save file:", file=save_manager.get_current_savefile_as_discord_file())
        except comm_except as err:
            await ctx.respond(str(err))

    @slash_command(name="undo", description="Undo your mistakes")
    async def undo(self, ctx: BridgeExtContext, amount: int = 1):
        try:
            await ctx.respond(cfuncs.undo_command(amount))
        except comm_except as err:
            await ctx.respond(str(err))

    @slash_command(name="redo", description="Redo your undone non-mistakes")
    async def redo(self, ctx: BridgeExtContext, amount: int = 1):
        try:
            await ctx.respond(cfuncs.redo_command(amount))
        except comm_except as err:
            await ctx.respond(str(err))

    @commands.command(name="save")
    async def save_command(self, ctx: BridgeExtContext):
        try:
            save_manager.check_file_loaded(raise_error=True)
            save_manager.save()
            await ctx.respond("saved")
        except comm_except as err:
            await ctx.respond(str(err))


def setup(bot: Bot):
    cmp_hlp.check_base_setup()
    bot.add_cog(CampaignCog())

    print("campaign extension loaded\n")
