import logging

from discord.ext import commands
from discord.ui import View, button, Button
from discord import ApplicationContext, PartialEmoji, ButtonStyle as Bstyle, Interaction

from .weather import WeatherTracker, init_data, find_weather_data_values_from_fields
from ...command_helper_functions import bot_channel_permissions_check, MESSAGE_DELETION_DELAY, edit_interaction_message

logger = logging.getLogger('bot')


class WeatherCog(commands.Cog):

    @commands.slash_command(name="weather", description="Start a new Weather track.")
    async def weather(self, ctx: ApplicationContext):
        if not await bot_channel_permissions_check(ctx):
            return

        weather_tracker = WeatherTracker(0, 0, 0)
        view = WeatherView(weather_tracker)
        await ctx.respond(view=view, embed=weather_tracker.get_weather_tracker_embed())


class WeatherView(View):

    def __init__(self, weather_tracker: WeatherTracker = None):
        super().__init__(timeout=None)
        self.weather_tracker = weather_tracker
        logger.debug("WeatherView created")

    @button(label="roll", style=Bstyle.primary, row=0, emoji=PartialEmoji.from_str("☁"), custom_id="roll_weather")
    async def roll_weather(self, _: Button, interaction: Interaction):
        self.update_weather_data(interaction)
        text_delta = self.weather_tracker.roll()

        await edit_interaction_message(
            interaction,
            {
                "embed": self.weather_tracker.get_weather_tracker_embed(text_delta),
                "view": self
            }
        )

    def update_weather_data(self, interaction: Interaction):
        val = find_weather_data_values_from_fields(interaction.message.embeds[0])
        self.weather_tracker = WeatherTracker(int(val[0]), int(val[1]), int(val[2]))


def setup(bot: commands.Bot):
    init_data()
    # Every extension should have this function
    bot.add_cog(WeatherCog())
    bot.add_view(WeatherView())
    logger.info("weather extension loaded")
