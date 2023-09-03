import logging
import os
from os.path import exists
from typing import Callable, Awaitable

import discord
from discord.ui import View, button, Button
from discord import ButtonStyle as Bstyle, Interaction, ApplicationContext, PartialEmoji

from . import packg_variables
from .packg_variables import message_deletion_delay
from ..ContextInfo import ContextInfo, initContext
from .SaveDataManagement import char_data_access as char_data, \
    live_save_manager as live_save, \
    save_file_management as save_manager
from .SaveDataManagement.char_data_access import get_char
from .campaign_exceptions import CommandException as ComExcept
from . import base_command_logic as bcom, \
    packg_variables as cmp_vars, \
    campaign_helper as cmp_hlp

logger = logging.getLogger('bot')


class SimpleStatModal(discord.ui.Modal):
    def __init__(self, char_tag=None, func=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.func = func
        self.char_tag = char_tag
        self.add_item(discord.ui.InputText(label="amount"))

    async def callback(self, interaction: discord.Interaction):
        await self.func(await initContext(interaction=interaction), int(self.children[0].value), self.char_tag)


class DamageModal(discord.ui.Modal):
    def __init__(self, char_tag=None, func=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.func = func
        self.char_tag = char_tag
        self.add_item(discord.ui.InputText(label="amount"))
        self.add_item(discord.ui.InputText(label="kills"))
        self.children[1].required = False

    async def callback(self, interaction: discord.Interaction):
        await self.func(
            await initContext(interaction=interaction),
            int(self.children[0].value),
            int(self.children[1].value) if self.children[1].value != "" else 0,
            self.char_tag
        )


class UndoView(View):
    def __init__(self, executing_user: str):
        super().__init__(timeout=600)
        self.executing_user = executing_user

    async def checkAuthorized(self, interaction: Interaction):
        if str(interaction.user.id) != self.executing_user:
            await (await interaction.response.send_message("you're not the same user that executed the button's command")).delete_original_response(delay=5)
            return False
        else:
            return True

    @button(label="undo", style=Bstyle.grey, row=2, emoji=PartialEmoji.from_str("↩"))
    async def button_callback7(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await undo(await initContext(interaction=interaction))

    @button(label="redo", style=Bstyle.grey, row=2, emoji=PartialEmoji.from_str("↪"))
    async def button_callback8(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await redo(await initContext(interaction=interaction))


class StatView(View):
    def __init__(self, executing_user:str, char_tag: str):
        super().__init__(timeout=600)
        self.char_tag = char_tag
        self.executing_user = executing_user

    async def checkAuthorized(self, interaction: Interaction):
        if str(interaction.user.id) != self.executing_user:
            await (await interaction.response.send_message("you're not the same user that executed the button's command")).delete_original_response(delay=5)
            return False
        else:
            return True

    @button(label="crit", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("🎯"))
    async def button_callback(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await crit(await initContext(interaction=interaction), char_tag=self.char_tag)

    @button(label="faint", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("💤"))
    async def button_callback1(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await faint(await initContext(interaction=interaction), char_tag=self.char_tag)

    @button(label="dodge", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("💨"))
    async def button_callback2(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await dodged(await initContext(interaction=interaction), char_tag=self.char_tag)

    @button(label="resisted", style=Bstyle.grey, row=1, emoji=PartialEmoji.from_str("🛡"))
    async def button_callback3(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await interaction.response.send_modal(SimpleStatModal(title="Resist Damage", func=take_reduced, char_tag=self.char_tag))

    @button(label="take", style=Bstyle.grey, row=1, emoji=PartialEmoji.from_str("🩸"))
    async def button_callback4(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await interaction.response.send_modal(SimpleStatModal(title="Take Damage", func=take, char_tag=self.char_tag))

    @button(label="heal", style=Bstyle.grey, row=1, emoji=PartialEmoji.from_str("🚑"))
    async def button_callback5(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await interaction.response.send_modal(SimpleStatModal(title="Heals Damage", func=heal, char_tag=self.char_tag))

    @button(label="deal", style=Bstyle.grey, row=1, emoji=PartialEmoji.from_str("🗡"))
    async def button_callback6(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await interaction.response.send_modal(DamageModal(title="Deals Damage", func=cause, char_tag=self.char_tag))

    @button(label="undo", style=Bstyle.grey, row=2, emoji=PartialEmoji.from_str("↩"))
    async def button_callback7(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await undo(await initContext(interaction=interaction))

    @button(label="redo", style=Bstyle.grey, row=2, emoji=PartialEmoji.from_str("↪"))
    async def button_callback8(self, _: Button, interaction: Interaction):
        if await self.checkAuthorized(interaction):
            await redo(await initContext(interaction=interaction))


async def catch_and_respond_char_action(
        ctx: ContextInfo,
        char_tag: str, func: Callable[[str, str], str],
        send_char_view=False,
        timeout=-1) -> bool:
    """
    Wraps a character specific command function, executing it with the user_id gained from the context.
    Also if char_tag is None, it will try to load the character name from the current file

    :param ctx: The message context
    :param func: the function executed
    :param char_tag: the char_tag of the character that the command applies to
    :param send_char_view: determines whether the character editing view is sent after execution
    :param timeout: determines how long it takes for the response to dissappear. Set to None if it shouldn't disappear
    """
    executing_user = str(ctx.author.id)
    if timeout == -1:  # set to package default
        timeout = message_deletion_delay
    try:
        if char_tag is None:
            char_tag = char_data.get_char_tag_by_id(executing_user)
        if send_char_view:
            await ctx.respond(func(executing_user, char_tag), view=StatView(executing_user, char_tag), delay=timeout)
        else:
            await ctx.respond(func(executing_user, char_tag), view=UndoView(executing_user), delay=timeout)
        return True
    except ComExcept as err:
        await ctx.respond(err)
        return False


async def catch_and_respond_file_action(
        ctx: ContextInfo,
        func: Callable[[str], str],
        timeout: int = -1,
        send_undo_view=True) -> bool:
    """
    Wraps a file specific command function, executing it with the user_id gained from the context.

    :param ctx: The message context
    :param func: the function executed
    :param timeout: determines how long it takes for the response to dissappear. Set to None if it shouldn't disappear
    :param send_undo_view: determines whether the undo view should be sent after execution
    """
    executing_user = str(ctx.author.id)
    if timeout == -1:  # set to package default
        timeout = message_deletion_delay
    try:
        if send_undo_view:
            await ctx.respond(func(executing_user), view=UndoView(executing_user), delay=timeout)
        else:
            await ctx.respond(func(executing_user), delay=timeout)
        return True
    except ComExcept as err:
        await ctx.respond(err)
        return False


async def catch_async_file_action(ctx: ContextInfo, func: Callable[[str], Awaitable[None]], send_undo_view=True) -> bool:
    """
        Wraps a file specific command function, executing it with the user_id gained from the context.
        This is the async version

        :param func: the function executed
        :param ctx: The message context
        :param send_undo_view: determines whether the undo view should be sent after execution
        """
    executing_user = str(ctx.author.id)
    try:
        await func(executing_user)
        if send_undo_view:
            await ctx.respond("", view=UndoView(executing_user))
        return True
    except ComExcept as err:
        await ctx.respond(err)
        return False


async def edit_char_view(ctx: ContextInfo, char_tag: str) -> bool:
    val = await catch_and_respond_char_action(ctx,
                                              char_tag,
                                              lambda executing_user, tag: f"**{get_char(executing_user, tag).name}**",
                                              send_char_view=True,
                                              timeout=None)
    return val


async def add_c(ctx: ContextInfo, char_tag: str, char_name: str, user_id: str = None) -> bool:
    val = await catch_and_respond_file_action(ctx,
                                              lambda executing_user: bcom.add_char(executing_user, char_tag, char_name)
                                              )
    if user_id is not None:
        val = val and await claim(ctx, char_tag, user_id)
    return val


async def rem_c(ctx: ContextInfo, char_tag: str) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.rem_char(executing_user, char_tag))


async def crit(ctx: ContextInfo, amount: int = 1, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.crit(executing_user, tag, amount))


async def faint(ctx: ContextInfo, amount: int = 1, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.faint(executing_user, tag, amount))


async def dodged(ctx: ContextInfo, amount: int = 1, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.dodge(executing_user, tag, amount))


async def cause(ctx: ContextInfo, amount: int, kills: int = 0, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.cause_damage(executing_user, tag,
                                                                                             amount, kills))


async def take(ctx: ContextInfo, amount: int, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.take_damage(executing_user, tag, amount,
                                                                                            False))


async def take_reduced(ctx: ContextInfo, amount: int, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.take_damage(executing_user, tag, amount,
                                                                                            True))


async def heal(ctx: ContextInfo, amount: int, char_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               char_tag,
                                               lambda executing_user, tag: bcom.heal(executing_user, tag, amount))


async def log(ctx: ContextInfo, adv=False) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.log(executing_user, adv),
                                               timeout=None)


async def retag_pc(ctx: ContextInfo, char_tag_old: str, char_tag_new: str) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.retag_character(executing_user, char_tag_old,
                                                                                           char_tag_new))


async def rename_pc(ctx: ContextInfo, char_tag: str, new_char_name: str) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.rename_character(executing_user, char_tag,
                                                                                            new_char_name))


async def load_command(ctx: ContextInfo, file_name: str) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.load_or_create_save(executing_user,
                                                                                               file_name))


async def add_player(ctx: ContextInfo, user_id: str) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.add_player(executing_user, user_id))


async def rem_player(ctx: ContextInfo, user_id: str) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.remove_player(executing_user, user_id))


async def claim(ctx: ContextInfo, char_tag: str, user_id: str = None) -> bool:
    return await catch_async_file_action(ctx,
                                         lambda executing_user: bcom.claim_character(executing_user, ctx, char_tag,
                                                                                     user_id))


async def unclaim(ctx: ContextInfo, character_tag: str = None) -> bool:
    return await catch_and_respond_char_action(ctx,
                                               character_tag,
                                               lambda executing_user, tag: bcom.unclaim_char(executing_user, tag))


async def session(ctx: ContextInfo) -> bool:
    executing_user = str(ctx.author.id)
    try:
        # this is not wrapped in catch and respond, cause in case of it not working, it should not send a message
        await bcom.cache_file(executing_user, ctx)
    except ComExcept:
        pass
    return await catch_and_respond_file_action(ctx,
                                               lambda exec_user: bcom.session_increase(exec_user))


async def cache(ctx: ContextInfo) -> bool:
    return await catch_async_file_action(ctx,
                                         lambda executing_user: bcom.cache_file(executing_user, ctx))


async def get_cache(ctx: ContextInfo) -> bool:
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
            bcom.session_increase(str(ctx.author.id))
            return True

        if save_manager.compare_savefile_novelty_by_path(local_save_path, cache_save_path) == -1:
            os.remove(local_save_path)
            os.rename(cache_save_path, local_save_path)
            live_save.load_file_into_memory(filename, replace=True)
            await ctx.respond("replaced")
            await load_command(ctx, file_name=filename)
            bcom.session_increase(str(ctx.author.id))
        else:
            os.remove(cache_save_path)
            await ctx.respond("already up to date")
        return True
    except ComExcept as err:
        await ctx.respond(str(err))
        return False


async def download(ctx: ApplicationContext) -> bool:
    executing_user = str(ctx.author.id)
    try:
        live_save.check_file_loaded(executing_user, raise_error=True)
        file_name = live_save.get_loaded_filename(executing_user)
        await ctx.respond("save file:", file=save_manager.get_savefile_as_discord_file(file_name))
        return True
    except ComExcept as err:
        await ctx.respond(str(err))
        return False


async def undo(ctx: ContextInfo, amount: int = 1) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.undo_command(executing_user, amount))


async def redo(ctx: ContextInfo, amount: int = 1) -> bool:
    return await catch_and_respond_file_action(ctx,
                                               lambda executing_user: bcom.redo_command(executing_user, amount))
