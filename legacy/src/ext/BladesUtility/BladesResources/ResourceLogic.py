import logging
import os

from discord import Embed, PartialEmoji, ButtonStyle as Bstyle, Interaction, File, SelectOption
from discord.ui import View, button, Button, Select

from .ResourceSpriteBuilding import build_stress_track_image, delete_merged_image
from .ResourceTracker import ResourceTracker
from ....ContextInfo import ContextInfo
from ....command_helper_functions import edit_interaction_message


logger = logging.getLogger('bot')


def create_resource_tracker_from_fields(embed: Embed):
    clean_desc = embed.description.replace("*", "").replace("_", "").split(":")[1].strip()
    resource_info = clean_desc.split("/")
    return ResourceTracker(int(resource_info[0]), int(resource_info[1]))


def get_stress_tracker_embed(stress_tracker: ResourceTracker):
    file_path = build_stress_track_image(stress_tracker)

    embed = Embed(title=f'Stress Track')
    embed.description = f'Stress: {stress_tracker.value}/{stress_tracker.max_resource}'
    embed.set_image(url='attachment://merged.png')
    return embed, file_path


async def send_stress_tracker(ctx: ContextInfo, stress_tracker: ResourceTracker):
    embed, file_path = get_stress_tracker_embed(stress_tracker)
    file = File(file_path)
    await ctx.respond(embed=embed, file=file, view=ResourceView(stress_tracker))
    os.remove(file_path)


class ResourceView(View):

    def __init__(self, resource_tracker: ResourceTracker = None):
        super().__init__(timeout=None)
        self.resource_tracker = resource_tracker

    def update_resource_data(self, interaction: Interaction):
        self.resource_tracker = create_resource_tracker_from_fields(interaction.message.embeds[0])

    @button(style=Bstyle.gray, row=0, emoji=PartialEmoji.from_str("◀"), custom_id="reduce")
    async def reduce(self, _: Button, interaction: Interaction):
        await self.change_value(False, interaction)

    @button(style=Bstyle.gray, row=0, emoji=PartialEmoji.from_str("▶"),
            custom_id="increase")
    async def increase(self, _: Button, interaction: Interaction):
        await self.change_value(True, interaction)

    @button(label="set stress", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("⚙"),
            custom_id="set_stress")
    async def set_stress(self, _: Button, interaction: Interaction):

        self.update_resource_data(interaction)
        embed, file_path = get_stress_tracker_embed(self.resource_tracker)
        view = ResourceView(resource_tracker=self.resource_tracker)
        options = []
        for val in range(self.resource_tracker.max_resource+1):
            options.append(
                SelectOption(
                    default=(val == self.resource_tracker.value),
                    label=str(val)
                )
            )

        stress_select = Select(options=options, custom_id='select_stress_dropdown')

        async def selection_made(interaction: Interaction):
            self.update_resource_data(interaction)
            self.resource_tracker.set_value(int(stress_select.values[0]))
            embed, file_path = get_stress_tracker_embed(self.resource_tracker)
            new_view = ResourceView(resource_tracker=self.resource_tracker)
            await edit_interaction_message(
                interaction,
                {
                    "embed": embed,
                    "view": new_view,
                    "file": File(file_path)
                }
            )
            delete_merged_image()
            self.stop()

        stress_select.callback = selection_made
        view.add_item(stress_select)
        await edit_interaction_message(
            interaction,
            {
                "embed": embed,
                "view": view,
                "file": File(file_path)
            }
        )
        delete_merged_image()
        self.stop()

    @button(label="reduce max", style=Bstyle.gray, row=1, emoji=PartialEmoji.from_str("◀"), custom_id="reduce_max")
    async def reduce_max(self, _: Button, interaction: Interaction):
        await self.change_max(False, interaction)

    @button(label="increase max", style=Bstyle.gray, row=1, emoji=PartialEmoji.from_str("▶"),
            custom_id="increase_max")
    async def increase_max(self, _: Button, interaction: Interaction):
        await self.change_max(True, interaction)

    async def change_value(self, increase: bool, interaction: Interaction):
        self.update_resource_data(interaction)
        self.resource_tracker.set_value(self.resource_tracker.value + (1 if increase else -1))
        embed, file_path = get_stress_tracker_embed(self.resource_tracker)
        await edit_interaction_message(
            interaction,
            {
                "embed": embed,
                "view": ResourceView(resource_tracker=self.resource_tracker),
                "file": File(file_path)
            }
        )
        delete_merged_image()
        self.stop()

    async def change_max(self, increase: bool, interaction: Interaction):
        self.update_resource_data(interaction)
        self.resource_tracker.set_max_value(self.resource_tracker.max_resource + (1 if increase else -1))
        embed, file_path = get_stress_tracker_embed(self.resource_tracker)
        await edit_interaction_message(
            interaction,
            {
                "embed": embed,
                "view": ResourceView(resource_tracker=self.resource_tracker),
                "file": File(file_path)
            }
        )
        delete_merged_image()
        self.stop()
