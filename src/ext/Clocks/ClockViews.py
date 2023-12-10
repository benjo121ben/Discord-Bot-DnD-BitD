import logging

from discord import Interaction, ButtonStyle as Bstyle, PartialEmoji, Embed, File, InteractionResponded, Member
from discord.ui import View, button, Button

from ... import GlobalVariables as global_vars
from .MessageContent.AbstractMessageContent import AbstractMessageContent
from .clock_data import get_clock_image, NoClockImageException, Clock, load_clocks
from .clock_logic import tick_clock_logic, remove_clock_logic, MESSAGE_DELETION_DELAY
from ..ContextInfo import ContextInfo, initContext

logger = logging.getLogger('bot')
BUTTON_VIEW_TIMEOUT: int = 21600  # 6 hours

# TODO use this error message everywhere in the code where the user gets a unknown error/interaction failed
error_message = "An error has occurred. Try re-inviting the bot to your server through the button in its description, " \
                "the issue may be due to updated required permissions. Sorry for the inconvenience\n" \
                "If the issue persists even after a re-invite, please send my creator an error message with a screenshot and describe your problem.\n" \
                "**Use the discord linked in the \\help command.\n**" \
                "Error:\n"


async def bot_channel_permissions_check_interaction(interaction: Interaction):
    if interaction.guild is None:
        return True

    member_data: Member = interaction.guild.get_member(global_vars.bot.user.id)
    if not interaction.channel.permissions_for(member_data).view_channel:
        await (await initContext(interaction=interaction)).respond(
            "The bot does not have permission to view this channel.\n"
            "Some stuff just doesn't work without it, so please make sure you give it access. :)",
            delay=40
        )


class MessageData:
    channel_id: int = 0
    message_id: int = 0

    def __init__(self, channel_id: int, message_id: int):
        self.message_id = message_id
        self.channel_id = channel_id

    def __str__(self):
        return f"[MessageData: {{channel_id:{self.channel_id} | message_id:{self.message_id}}}]"


def get_clock_response_params(clock: Clock, assiciated_user: str) -> dict:
    embed = Embed(title=f'**{clock.name}**')
    params = {
        "file": None,
        "embed": embed,
        "view": ClockAdjustmentView(clock_tag=clock.tag, associated_user=assiciated_user)
    }
    try:
        image_file: File = get_clock_image(clock)
        embed.set_thumbnail(url=f'attachment://{image_file.filename}')
        params["file"] = image_file
        embed.description = f"_Tag: {clock.tag}_"
    except NoClockImageException:
        embed.set_footer(text="Clocks of this size don't have output images")
        embed.description = f'Tag: _{clock.tag}_ : {{{clock.ticks}/{clock.size}}}'
        logger.debug(
            f"clock of size {clock.size} was printed without image, make sure images are included for all sizes needed."
        )
    no_none_params = {k: v for k, v in params.items() if v is not None}  # removes all parameters that are none

    return no_none_params


class ClockAdjustmentView(View):

    def __init__(self, clock_tag: str, associated_user: str, message_data: MessageData = None):
        super().__init__(timeout=BUTTON_VIEW_TIMEOUT)
        self.clock_tag = str(clock_tag)
        self.associated_user = str(associated_user)
        self.message_data = message_data

        logger.debug("ClockAdjustmentView created: [clock_tag={0}, associated_user={1}, message_data={2}]"
                     .format(self.clock_tag, self.associated_user, self.message_data))
        logger.debug(f"type associated user: {type(self.associated_user)}")

    def log_view_interaction(self, interaction_name: str, interaction: Interaction):
        logger.debug("{0} called: ClockAdjustmentView[interaction ID={1}, clock_tag={2}, associated_user={3}, message_data={4}]"
                     .format(interaction_name, interaction.user.id, self.clock_tag, self.associated_user, self.message_data))
        logger.debug(f"type associated user: {type(self.associated_user)}")

    async def on_timeout(self) -> None:
        message = await self.get_message()
        if message is not None:
            await message.edit(view=LockedClockAdjustmentView())
        self.stop()

    def update_view_data(self, interaction: Interaction):
        if not interaction.message:
            raise Exception("could not gather data from the interaction")
        self.clock_tag = interaction.message.embeds[0].description.split(":")[1].strip().replace("_", "")
        self.associated_user = str(interaction.message.interaction.data['user']['id'])
        self.message = interaction.message
        return self.clock_tag, self.associated_user

    async def get_message(self):
        if self.message:
            logger.debug("message present")
            return self.message
        elif self.message_data is not None:
            logger.debug("fetching message")
            return await (
                    await global_vars.bot.fetch_channel(self.message_data.channel_id)
                ).fetch_message(self.message_data.message_id)
        else:
            logger.debug("message not present")
            return None

    def refresh_clock_data(self, interaction: Interaction):
        new_clock_tag = interaction.message.embeds[0].description.split(":")[1].strip().replace("_", "")
        new_associated_user = str(interaction.message.interaction.data['user']['id'])
        if new_clock_tag != self.clock_tag or new_associated_user != self.associated_user:
            logger.debug("There was a discrepancy in the data")
            logger.debug(f"[old | new] clock_tag: [{self.clock_tag}, {new_clock_tag}]")
            logger.debug(f"[old | new] associated_user: [{self.associated_user}, {new_associated_user}]")
            self.clock_tag = new_clock_tag
            self.associated_user = new_associated_user

    @button(label="tick", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("▶"), custom_id="plus_tick_button")
    async def button_tick_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        self.log_view_interaction("tick", interaction)
        ctx: ContextInfo = await initContext(interaction=interaction)
        try:
            params: AbstractMessageContent = tick_clock_logic(clock_tag=self.clock_tag, executing_user=self.associated_user, ticks=1)
            await edit_interaction_message(interaction, params.get_message_content(get_clock_response_params))
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message +
                              str(e))

    @button(label="back_tick", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("◀"), custom_id="minus_tick_button")
    async def button_back_tick_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        self.log_view_interaction("back_tick", interaction)
        ctx: ContextInfo = await initContext(interaction=interaction)
        try:
            params: AbstractMessageContent = tick_clock_logic(clock_tag=self.clock_tag, executing_user=self.associated_user, ticks=-1)
            await edit_interaction_message(interaction, params.get_message_content(get_clock_response_params))
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message +
                              str(e))

    @button(label="delete", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("🚮"), custom_id="delete_button")
    async def button_delete_callback(self, _: Button, interaction: Interaction):
        if not bot_channel_permissions_check_interaction(interaction):
            return
        self.refresh_clock_data(interaction)
        self.log_view_interaction("delete", interaction)
        ctx: ContextInfo = await initContext(interaction=interaction)
        try:
            params: AbstractMessageContent = remove_clock_logic(clock_tag=self.clock_tag, executing_user=self.associated_user)
            await ctx.respond(**params.get_message_content(get_clock_response_params))
            await interaction.message.delete()
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message +
                              str(e))

    @button(label="lock view", style=Bstyle.red, row=1, emoji=PartialEmoji.from_str("🔒"), custom_id="lock_view_button")
    async def button_lock_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        self.log_view_interaction("lock view", interaction)
        ctx: ContextInfo = await initContext(interaction=interaction)
        try:
            self.refresh_clock_data(interaction)
            await edit_interaction_message(
                interaction,
                {"view": LockedClockAdjustmentView()}
            )
            global_vars.bot.add_view(LockedClockAdjustmentView())
            self.stop()
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message +
                              str(e))


class LockedClockAdjustmentView(View):
    def __init__(self):
        super().__init__(timeout=None)
        logger.debug("LockedClockAdjustmentView created")

    @staticmethod
    def log_view_interaction(interaction_name: str, interaction: Interaction):
        logger.debug("{0} called: LockedClockAdjustmentView[interaction ID={1}]"
                     .format(interaction_name, interaction.user.id))

    @button(label="unlock view", style=Bstyle.primary, row=0, emoji=PartialEmoji.from_str("🔓"), custom_id="unlock_clock_button")
    async def button_lock_callback(self, _: Button, interaction: Interaction):
        clock_tag = interaction.message.embeds[0].description.split(":")[1].strip().replace("_", "")
        associated_user = str(interaction.message.interaction.data['user']['id'])
        logger.debug(f"unlock_called for message {interaction.message.id}. Tag={clock_tag}. Assoc_user={associated_user}")
        if str(interaction.user.id) != associated_user:
            self.log_view_interaction("LockedClockAdjustmentView/unlock_view, not owner", interaction)
            await (await initContext(interaction=interaction)).respond("You are not the owner of this clock", delay=10)
            return
        id = interaction.message.id
        message_data = MessageData(interaction.channel.id, id)

        if clock_tag not in load_clocks(associated_user):
            await edit_interaction_message(
                interaction,
                {"content": "This Clock does not exist anymore", "view": None, "delay": MESSAGE_DELETION_DELAY}
            )
            global_vars.bot.add_view(LockedClockAdjustmentView())
        else:
            await edit_interaction_message(
                interaction,
                {"view": ClockAdjustmentView(clock_tag, associated_user, message_data)}
            )
            global_vars.bot.add_view(LockedClockAdjustmentView())
            self.stop()


# This will be deprecated in a future update of py-cord, which introduces interaction.respond and interaction.edit
# I'm making my own shorthand since I haven't yet figured out how to get access to that code
async def edit_interaction_message(interaction: Interaction, params: dict):
    if 'delay' in params:
        params['delete_after'] = params['delay']
        del params['delay']
    try:
        if not interaction.response.is_done():
            await interaction.response.edit_message(**params)
            return await interaction.original_response()
        else:
            return await interaction.edit_original_response(**params)
    except InteractionResponded:
        return await interaction.edit_original_response(**params)