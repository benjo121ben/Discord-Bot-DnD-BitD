import logging
import os
from os.path import exists

import discord.errors as d_errors
from discord import slash_command
from discord.ext import commands
from discord.ext.bridge import BridgeExtContext, Bot

from .SaveDataManagement import char_data_access as char_data
from . import packg_variables
from .campaign_exceptions import CommandException as ComExcept
from . import Undo, CommandFunctions as CFuncs, \
    packg_variables as cmp_vars, \
    campaign_helper as cmp_hlp
from .SaveDataManagement import save_file_management as save_manager, live_save_manager as live_save

logger = logging.getLogger('bot')


async def catch_and_respond_char_action(ctx: BridgeExtContext, char_tag: str, func):
    executing_user = str(ctx.author.id)
    try:
        if char_tag is None:
            char_tag = char_data.get_char_tag_by_id(executing_user)
        await ctx.respond(func(executing_user, char_tag))
    except ComExcept as err:
        await ctx.respond(err)


async def catch_and_respond_file_action(ctx: BridgeExtContext, func):
    executing_user = str(ctx.author.id)
    try:
        await ctx.respond(func(executing_user))
    except ComExcept as err:
        await ctx.respond(err)


class CampaignCog(commands.Cog):

    @slash_command(name="crit", description="Character has rollet a nat20")
    async def crit(self, ctx: BridgeExtContext, char_tag: str = None):
        await catch_and_respond_char_action(ctx,
                                            char_tag,
                                            lambda executing_user, tag: CFuncs.crit(executing_user, tag))

    @slash_command(name="dodged", description="Character dodged an attack")
    async def dodged(self, ctx: BridgeExtContext, char_tag: str = None):
        await catch_and_respond_char_action(ctx,
                                            char_tag,
                                            lambda executing_user, tag: CFuncs.dodge(executing_user, tag))

    @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: BridgeExtContext, amount: int, kills: int = 0, char_tag: str = None):
        await catch_and_respond_char_action(ctx,
                                            char_tag,
                                            lambda executing_user, tag: CFuncs.cause_damage(executing_user, char_tag, amount, kills))

    @slash_command(name="take",
                   description="Character takes all damage")
    async def take(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        await catch_and_respond_char_action(ctx,
                                            char_tag,
                                            lambda executing_user, tag: CFuncs.take_damage(executing_user, char_tag, amount, False))

    @slash_command(name="taker",
                   description="Character takes reduced damage")
    async def take_reduced(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        await catch_and_respond_char_action(ctx,
                                            char_tag,
                                            lambda executing_user, tag: CFuncs.take_damage(executing_user, char_tag, amount, True))

    @slash_command(
        name="heal",
        description="Character heals another by amount. Increases damage_healed stat"
    )
    async def heal(self, ctx: BridgeExtContext, amount: int, char_tag: str = None):
        amount = abs(amount)
        await catch_and_respond_char_action(ctx,
                                            char_tag,
                                            lambda executing_user, tag: CFuncs.heal(executing_user, char_tag, amount))

    @slash_command(name="log", description="Outputs all current Character information")
    async def log(self, ctx: BridgeExtContext, adv=False):
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.log(executing_user, adv))

    @slash_command(
        name="add_char",
        description="Add Character to save file. If user_id is provided, it tries to claim the character for that user"
    )
    async def add_c(self, ctx: BridgeExtContext, char_tag: str, char_name: str, user_id: str = None):
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.add_char(executing_user, char_tag, char_name))
        if user_id is not None:
            await self.claim(ctx, char_tag, user_id)

    @slash_command(
        name="retag_char",
        description="Retag a character on the current save file."
    )
    async def retag_player_character(self, ctx: BridgeExtContext, char_tag_old: str, char_tag_new: str):
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.retag_character(executing_user, char_tag_old, char_tag_new))

    @slash_command(
        name="load",
        description="Load an existing campaign save file or create a new one"
    )
    async def load_command(self, ctx: BridgeExtContext, file_name: str):
        print("LOADED")
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.load_or_create_save(executing_user, file_name))

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: BridgeExtContext, char_tag: str, user_id: str = None):
        executing_user = str(ctx.author.id)
        try:
            if user_id is None:
                user_id = str(ctx.author.id)
            CFuncs.claim_character(executing_user, char_tag, user_id)
        except ComExcept as err:
            await ctx.respond(str(err))
            return

        user = None
        try:
            user = await cmp_hlp.get_bot().fetch_user(user_id)
        except d_errors.NotFound as err:
            logger.error(err)
            await ctx.respond("A user with this ID could not be found by the bot.\n"
                              "Make sure the bot shares a server with the user that has this ID")
            Undo.undo(executing_user)
            Undo.discard_undo_queue_after_pointer(executing_user)
            return
        await ctx.respond(f"{char_tag} assigned to {user.name}")

    @slash_command(name="unclaim", description="Unclaim an assigned Character")
    async def unclaim(self, ctx: BridgeExtContext, character_tag: str = None):
        await catch_and_respond_char_action(ctx,
                                            character_tag,
                                            lambda executing_user, tag: CFuncs.unclaim_char(executing_user, tag))

    @slash_command(name="session", description="increase session counter by 1")
    async def session(self, ctx: BridgeExtContext):
        await self.cache(ctx)
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.session_increase(executing_user))

    @slash_command(name="cache", description="Admin command: caches the last save file into the provided server chat")
    async def cache(self, ctx: BridgeExtContext):
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.cache_file(ctx, executing_user))

    @slash_command(name="get_cache", description="Admin command: tries to download the latest save from cache server chat")
    async def get_cache(self, ctx: BridgeExtContext):
        try:
            cmp_hlp.check_bot_admin(ctx, raise_error=True)
            chat_id = cmp_vars.cache_folder
            if chat_id is None:
                raise ComExcept("No cloudsavechannel id assigned")

            message = await cmp_hlp.get_bot().get_channel(chat_id).history(limit=1).next()
            filename = message.attachments[0].filename
            cache_save_path = packg_variables.get_cache_folder_filepath() + f'{os.sep}' + filename
            local_save_path = packg_variables.get_save_folder_filepath() + f'{os.sep}' + filename

            await message.attachments[0].save(fp=cache_save_path)
            if not exists(local_save_path):
                os.rename(cache_save_path, local_save_path)
                await ctx.respond(f"No local version found. Save {filename} has been imported.")
                return

            if save_manager.compare_savefile_novelty(local_save_path, cache_save_path) == -1:
                os.remove(local_save_path)
                os.rename(cache_save_path, local_save_path)
                live_save.load_file_into_memory(filename, replace=True)
                CFuncs.session_increase(str(ctx.author.id))
                await ctx.respond("replaced")
            else:
                os.remove(cache_save_path)
                await ctx.respond("already up to date")
        except ComExcept as err:
            await ctx.respond(str(err))

    @slash_command(name="download", description="Downloads the loaded savefile")
    async def download(self, ctx: BridgeExtContext):
        executing_user = str(ctx.author.id)
        try:
            live_save.check_file_loaded(executing_user, raise_error=True)
            file_name = live_save.get_loaded_filename(executing_user)
            await ctx.respond("save file:", file=save_manager.get_savefile_as_discord_file(file_name))
        except ComExcept as err:
            await ctx.respond(str(err))

    @slash_command(name="undo", description="Undo your mistakes")
    async def undo(self, ctx: BridgeExtContext, amount: int = 1):
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.undo_command(executing_user, amount))

    @slash_command(name="redo", description="Redo your undone non-mistakes")
    async def redo(self, ctx: BridgeExtContext, amount: int = 1):
        await catch_and_respond_file_action(ctx,
                                            lambda executing_user: CFuncs.redo_command(executing_user, amount))


def setup(bot: Bot):
    cmp_hlp.check_base_setup()
    bot.add_cog(CampaignCog())

    logger.info("campaign extension loaded\n")
