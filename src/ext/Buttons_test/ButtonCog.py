import logging

from discord.ui import View, button, Button
from discord import Embed, File, ButtonStyle as Bstyle, Interaction
from discord.ext.commands import slash_command, Cog
from discord.ext import bridge
from discord.ext.bridge import BridgeExtContext

logger = logging.getLogger('bot')


class TestView(View):
    def __init__(self, char_tag: str):
        super().__init__()
        self.char_tag = char_tag

    @button(label="Test", style=Bstyle.primary)
    async def button_callback(self, buttonInfo: Button, interaction: Interaction):
        await interaction.response.send_message(buttonInfo.view.char_tag)


class ButtonCog(Cog):
    @slash_command(name="test_button")
    async def testButton(self, ctx: BridgeExtContext):
        await ctx.respond("ButtonTest", view=TestView("fez"))


def setup(bot: bridge.Bot):
    # Every extension should have this function
    bot.add_cog(ButtonCog())
    logger.info("test extension loaded\n")