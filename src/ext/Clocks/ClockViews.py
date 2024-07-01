import logging

from discord import Interaction, ButtonStyle as Bstyle, PartialEmoji, Embed, File
from discord.ui import View, button, Button, Modal, InputText

from ...command_helper_functions import channel_perm_check_interaction, edit_interaction_message
from .clock_data import get_clock_image, NoClockImageException, Clock
from ...ContextInfo import ContextInfo, init_context

logger = logging.getLogger('bot')
BUTTON_VIEW_TIMEOUT: int = 21600  # 6 hours

# TODO use this error message everywhere in the code where the user gets a unknown error/interaction failed
error_message = "An error has occurred. Try re-inviting the bot to your server through the button in its description, " \
                "the issue may be due to updated required permissions. Sorry for the inconvenience.\n" \
                "If the issue persists even after a re-invite, please send my creator an error message with a screenshot and describe your problem.\n" \
                "**Use the discord linked in the /help command.\n**" \
                "Error:\n"


def get_clock_response_params(clock: Clock) -> dict:
    embed = Embed(title=f'**{clock.name}**')
    params = {
        "file": None,
        "embed": embed,
        "view": ClockAdjustmentView(clock)
    }
    embed.description = f'{{{clock.ticks}/{clock.size}}}'
    try:
        image_file: File = get_clock_image(clock)
        embed.set_thumbnail(url=f'attachment://{image_file.filename}')
        params["file"] = image_file
    except NoClockImageException:
        embed.set_footer(text="Clocks of this size don't have output images")
        logger.debug(
            f"clock of size {clock.size} was printed without image, make sure images are included for all sizes needed."
        )
    no_none_params = {k: v for k, v in params.items() if v is not None}  # removes all parameters that are none

    return no_none_params


class ClockAdjustmentView(View):

    def __init__(self, clock: Clock = None):
        super().__init__(timeout=None)
        self.clock = clock if clock is not None else Clock("", 4)

    def refresh_clock_data(self, interaction: Interaction):
        embed = interaction.message.embeds[0]
        cleaned_description = (embed.description
                               .replace("_", "")
                               .replace("{", "")
                               .replace("}", "")
                               .strip())
        new_clock_name = embed.title.replace("*", "").replace("_", "")
        new_clock_ticks = int(cleaned_description.split("/")[0])
        new_clock_size = int(cleaned_description.split("/")[1])
        self.clock = Clock(new_clock_name, new_clock_size, new_clock_ticks)

    @button(style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("◀"), custom_id="minus_tick_button")
    async def button_back_tick_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        self.clock.tick(-1)

        await update_interaction_clock(interaction, self.clock)

    @button(style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("▶"), custom_id="plus_tick_button")
    async def button_tick_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        self.clock.tick(1)
        await update_interaction_clock(interaction, self.clock)

    @button(style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("❌"), custom_id="delete_button")
    async def button_delete_callback(self, _: Button, interaction: Interaction):
        self.refresh_clock_data(interaction)
        try:
            await interaction.message.delete()
        except Exception as e:
            ctx: ContextInfo = await init_context(interaction=interaction)
            logger.error(e)
            await ctx.respond(error_message + str(e))

    @button(label="edit", style=Bstyle.primary, row=1, custom_id="clock_custom")
    async def clock_custom(self, _: Button, interaction: Interaction):
        custom_clock_modal = CustomClockModal(self.clock, title="Custom Clock")
        await interaction.response.send_modal(custom_clock_modal)


class SelectClockSizeView(View):
    def __init__(self, clock_title: str = ""):
        super().__init__(timeout=None)
        self.clock_title = clock_title

    @button(label="3", style=Bstyle.gray, row=0, custom_id="clock_3")
    async def clock_3(self, _: Button, interaction: Interaction):
        await self.create_clock(interaction, 3)

    @button(label="4", style=Bstyle.gray, row=0, custom_id="clock_4")
    async def clock_4(self, _: Button, interaction: Interaction):
        await self.create_clock(interaction, 4)

    @button(label="6", style=Bstyle.gray, row=0, custom_id="clock_6")
    async def clock_6(self, _: Button, interaction: Interaction):
        await self.create_clock(interaction, 6)

    @button(label="8", style=Bstyle.gray, row=0, custom_id="clock_8")
    async def clock_8(self, _: Button, interaction: Interaction):
        await self.create_clock(interaction, 8)

    @button(label="10", style=Bstyle.gray, row=0, custom_id="clock_10")
    async def clock_10(self, _: Button, interaction: Interaction):
        await self.create_clock(interaction, 10)

    @button(label="custom", style=Bstyle.primary, row=1, custom_id="clock_custom")
    async def clock_custom(self, _: Button, interaction: Interaction):
        clock = Clock(self.clock_title, 4)
        custom_clock_modal = CustomClockModal(clock, title="Custom Clock")
        await interaction.response.send_modal(custom_clock_modal)

    async def create_clock(self, interaction: Interaction, size: int):
        clock = Clock(self.clock_title, size)
        await update_interaction_clock(interaction, clock)


class CustomClockModal(Modal):
    def __init__(self, clock: Clock, failed=False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if(failed):
            self.title = "Input valid numbers for a new Clock"
        self.clock_name = clock.name
        self.add_item(InputText(label="size (> 0)", value=str(clock.size)))
        self.add_item(InputText(label="ticks (>= 0)", value=str(clock.ticks)))
        self.children[0].required = True
        self.children[1].required = True

    async def callback(self, interaction: Interaction):
        try:
            size = int(self.children[0].value)
            ticks = int(self.children[1].value)
            if ticks < 0 or size <= 0:
                await self.send_failed_modal(interaction)
            else:
                await update_interaction_clock(interaction, Clock(self.clock_name, size, ticks))
        except ValueError:
            await self.send_failed_modal(interaction)

    async def send_failed_modal(self, interaction: Interaction):
        embed = Embed()
        embed.title = self.clock_name
        embed.description = "**Please insert valid numbers for your custom clock**,\nor select a size for your clock"
        embed.set_footer(text="Custom clock sizes unfortunately have no fancy images")
        view = SelectClockSizeView(self.clock_name)
        try:
            if not await channel_perm_check_interaction(interaction):
                return

            await edit_interaction_message(interaction, {"embed": embed, "view": view})
        except Exception as e:
            ctx = await init_context(interaction=interaction)
            logger.error(e)
            await ctx.respond(error_message + str(e))
        self.stop()


async def update_interaction_clock(interaction: Interaction, clock: Clock):
    try:
        if not await channel_perm_check_interaction(interaction):
            return

        await edit_interaction_message(interaction, get_clock_response_params(clock))
    except Exception as e:
        ctx = await init_context(interaction=interaction)
        logger.error(e)
        await ctx.respond(error_message + str(e))
