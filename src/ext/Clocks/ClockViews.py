import logging

from discord import Interaction, ButtonStyle as Bstyle, PartialEmoji, Embed, File
from discord.ui import View, button, Button

from ...command_helper_functions import channel_perm_check_interaction, edit_interaction_message
from .MessageContent.AbstractMessageContent import AbstractMessageContent
from .clock_data import get_clock_image, NoClockImageException, Clock
from .clock_logic import tick_clock_logic
from ...ContextInfo import ContextInfo, init_context

logger = logging.getLogger('bot')
BUTTON_VIEW_TIMEOUT: int = 21600  # 6 hours

# TODO use this error message everywhere in the code where the user gets a unknown error/interaction failed
error_message = "An error has occurred. Try re-inviting the bot to your server through the button in its description, " \
                "the issue may be due to updated required permissions. Sorry for the inconvenience.\n" \
                "If the issue persists even after a re-invite, please send my creator an error message with a screenshot and describe your problem.\n" \
                "**Use the discord linked in the \\help command.\n**" \
                "Error:\n"


class MessageData:
    channel_id: int = 0
    message_id: int = 0

    def __init__(self, channel_id: int, message_id: int):
        self.message_id = message_id
        self.channel_id = channel_id

    def __str__(self):
        return f"[MessageData: {{channel_id:{self.channel_id} | message_id:{self.message_id}}}]"


def get_clock_response_params(clock: Clock) -> dict:
    embed = Embed(title=f'**{clock.name}**')
    params = {
        "file": None,
        "embed": embed,
        "view": ClockAdjustmentView(clock)
    }
    try:
        image_file: File = get_clock_image(clock)
        embed.set_thumbnail(url=f'attachment://{image_file.filename}')
        params["file"] = image_file
        embed.description = f'_{{{clock.ticks}/{clock.size}}}_'
    except NoClockImageException:
        embed.set_footer(text="Clocks of this size don't have output images")
        logger.debug(
            f"clock of size {clock.size} was printed without image, make sure images are included for all sizes needed."
        )
    no_none_params = {k: v for k, v in params.items() if v is not None}  # removes all parameters that are none

    return no_none_params


class ClockAdjustmentView(View):

    def __init__(self, clock: Clock):
        super().__init__(timeout=None)
        self.clock = clock

    def refresh_clock_data(self, interaction: Interaction):
        embed = interaction.message.embeds[0]
        cleaned_description = embed.description.replace("{", "").replace("}", "").strip()
        new_clock_name = embed.title.replace("*", "")
        new_clock_ticks = int(cleaned_description.split("/")[0])
        new_clock_size = int(cleaned_description.split("/")[1])
        self.clock = Clock(new_clock_name, new_clock_size, new_clock_ticks)

    @button(style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("◀"), custom_id="minus_tick_button")
    async def button_back_tick_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        ctx: ContextInfo = await init_context(interaction=interaction)
        try:
            params: AbstractMessageContent = tick_clock_logic(ticks=-1)
            await edit_interaction_message(interaction, params.get_message_content(get_clock_response_params))
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message + str(e))

    @button(style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("▶"), custom_id="plus_tick_button")
    async def button_tick_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        ctx: ContextInfo = await init_context(interaction=interaction)
        try:
            params: AbstractMessageContent = tick_clock_logic(ticks=1)
            await edit_interaction_message(interaction, params.get_message_content(get_clock_response_params))
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message + str(e))

    @button(style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("❌"), custom_id="delete_button")
    async def button_delete_callback(self, _: Button, interaction: Interaction):
        if not channel_perm_check_interaction(interaction):
            return
        self.refresh_clock_data(interaction)
        ctx: ContextInfo = await init_context(interaction=interaction)
        try:
            await interaction.message.delete()
        except Exception as e:
            logger.error(e)
            await ctx.respond(error_message + str(e))


class SelectClockSizeView(View):
    def __init__(self, clock_title: str = ""):
        super().__init__(timeout=None)
        self.clock_title = clock_title

    @button(label="4", style=Bstyle.primary, row=0, custom_id="clock_4")
    async def clock_4(self, _: Button, interaction: Interaction):
        clock = Clock(self.clock_title, 4)
        await edit_interaction_message(interaction, get_clock_response_params(clock))

    @button(label="6", style=Bstyle.primary, row=0, custom_id="clock_6")
    async def clock_6(self, _: Button, interaction: Interaction):
        clock = Clock(self.clock_title, 6)
        await edit_interaction_message(interaction, get_clock_response_params(clock))

    @button(label="8", style=Bstyle.primary, row=0, custom_id="clock_8")
    async def clock_8(self, _: Button, interaction: Interaction):
        clock = Clock(self.clock_title, 8)
        await edit_interaction_message(interaction, get_clock_response_params(clock))

    # @button(emoji="⚙", style=Bstyle.primary, row=0, custom_id="clock_custom")
    # async def clock_custom(self, _: Button, interaction: Interaction):
    #     clock = Clock(self.clock_title, 8)
    #     await edit_interaction_message(interaction, get_clock_response_params(clock))