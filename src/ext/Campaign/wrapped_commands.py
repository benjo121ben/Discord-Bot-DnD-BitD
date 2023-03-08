
import logging
import os
from os.path import exists

from discord.ext.bridge import BridgeExtContext

from . import packg_variables
from .SaveDataManagement import char_data_access as char_data, \
    live_save_manager as live_save, \
    save_file_management as save_manager
from .campaign_exceptions import CommandException as ComExcept
from . import base_command_logic as CFuncs, \
    packg_variables as cmp_vars, \
    campaign_helper as cmp_hlp

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


async def catch_async_file_action(ctx: BridgeExtContext, func):
    executing_user = str(ctx.author.id)
    try:
        await func(executing_user)
    except ComExcept as err:
        await ctx.respond(err)


async def crit(ctx: BridgeExtContext, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.crit(executing_user, tag))


async def faint(ctx: BridgeExtContext, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.faint(executing_user, tag))


async def dodged(ctx: BridgeExtContext, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.dodge(executing_user, tag))


async def cause(ctx: BridgeExtContext, amount: int, kills: int = 0, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.cause_damage(executing_user, tag, amount, kills))


async def take(ctx: BridgeExtContext, amount: int, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.take_damage(executing_user, tag, amount, False))


async def take_reduced(ctx: BridgeExtContext, amount: int, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.take_damage(executing_user, tag, amount, True))


async def heal(ctx: BridgeExtContext, amount: int, char_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        char_tag,
                                        lambda executing_user, tag: CFuncs.heal(executing_user, tag, amount))


async def log(ctx: BridgeExtContext, adv=False):
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.log(executing_user, adv))


async def add_c(ctx: BridgeExtContext, char_tag: str, char_name: str, user_id: str = None):
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.add_char(executing_user, char_tag, char_name))
    if user_id is not None:
        print("user_id =", user_id)
        await claim(ctx, char_tag, user_id)


async def retag_pc(ctx: BridgeExtContext, char_tag_old: str, char_tag_new: str):
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.retag_character(executing_user, char_tag_old, char_tag_new))


async def load_command(ctx: BridgeExtContext, file_name: str):
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.load_or_create_save(executing_user, file_name))


async def claim(ctx: BridgeExtContext, char_tag: str, user_id: str = None):
    print("IN WRAPPED CLAIM")
    await catch_async_file_action(ctx,
                                  lambda executing_user: CFuncs.claim_character(executing_user, ctx, char_tag, user_id))


async def unclaim(ctx: BridgeExtContext, character_tag: str = None):
    await catch_and_respond_char_action(ctx,
                                        character_tag,
                                        lambda executing_user, tag: CFuncs.unclaim_char(executing_user, tag))


async def session(ctx: BridgeExtContext):
    await cache(ctx)
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.session_increase(executing_user))


async def cache(ctx: BridgeExtContext):
    await catch_async_file_action(ctx,
                                  lambda executing_user: CFuncs.cache_file(executing_user, ctx))


async def get_cache(ctx: BridgeExtContext):
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
            await load_command(ctx, file_name=filename.split(save_manager.save_files_suffix)[0])
            CFuncs.session_increase(str(ctx.author.id))
            return

        if save_manager.compare_savefile_novelty_by_path(local_save_path, cache_save_path) == -1:
            os.remove(local_save_path)
            os.rename(cache_save_path, local_save_path)
            live_save.load_file_into_memory(filename, replace=True)
            await ctx.respond("replaced")
            await load_command(ctx, file_name=filename)
            CFuncs.session_increase(str(ctx.author.id))
        else:
            os.remove(cache_save_path)
            await ctx.respond("already up to date")
    except ComExcept as err:
        await ctx.respond(str(err))


async def download(ctx: BridgeExtContext):
    executing_user = str(ctx.author.id)
    try:
        live_save.check_file_loaded(executing_user, raise_error=True)
        file_name = live_save.get_loaded_filename(executing_user)
        await ctx.respond("save file:", file=save_manager.get_savefile_as_discord_file(file_name))
    except ComExcept as err:
        await ctx.respond(str(err))


async def undo(ctx: BridgeExtContext, amount: int = 1):
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.undo_command(executing_user, amount))


async def redo(ctx: BridgeExtContext, amount: int = 1):
    await catch_and_respond_file_action(ctx,
                                        lambda executing_user: CFuncs.redo_command(executing_user, amount))
