import logging

from discord.ext import commands
from discord.ui import View, button, Button, Select
from discord import ApplicationContext, PartialEmoji, ButtonStyle as Bstyle, Interaction, SelectOption

from .weather import WeatherTracker, init_data, create_weather_tracker_from_fields, get_titles
from ...command_helper_functions import channel_perm_check, edit_interaction_message

logger = logging.getLogger('bot')


class WeatherCog(commands.Cog):

    @commands.slash_command(name="weather", description="Start a new Weather track.")
    async def weather(self, ctx: ApplicationContext):
        if not await channel_perm_check(ctx):
            return

        weather_tracker = WeatherTracker(False, 0, 0, 0)
        view = WeatherView(weather_tracker)
        await ctx.respond(view=view, embed=weather_tracker.get_weather_tracker_embed())


class WeatherView(View):

    def __init__(self, weather_tracker: WeatherTracker = None):
        super().__init__(timeout=None)
        self.weather_tracker = weather_tracker

    def update_weather_data(self, interaction: Interaction):
        self.weather_tracker = create_weather_tracker_from_fields(interaction.message.embeds[0])

    @button(label="roll", style=Bstyle.primary, row=0, emoji=PartialEmoji.from_str("☁"), custom_id="roll_weather")
    async def roll_weather(self, _: Button, interaction: Interaction):
        await roll_dc_logic(self, interaction)

    @button(label="edit", style=Bstyle.green, row=0, emoji=PartialEmoji.from_str("✏"), custom_id="edit_weather")
    async def edit_weather(self, _: Button, interaction: Interaction):
        self.update_weather_data(interaction)
        await edit_interaction_message(
            interaction,
            {
                "embed": self.weather_tracker.get_weather_tracker_embed(),
                "view": WeatherSelectView(weather_tracker=self.weather_tracker)
            }
        )
        self.stop()

    @button(label="switch systems", style=Bstyle.gray, row=0, emoji=PartialEmoji.from_str("🗡"), custom_id="edit_system")
    async def switch_system_button(self, _: Button, interaction: Interaction):
        await switch_system(self, interaction)


class WeatherSelectView(View):
    def __init__(self, weather_tracker: WeatherTracker = None) -> None:
        super().__init__(timeout=None)
        self.weather_tracker = weather_tracker

        is_pathfinder = weather_tracker.is_pathfinder
        temp_titles, wind_titles, precip_titles = get_titles(is_pathfinder)
        temp_options = [
            SelectOption(
                label=val,
                value=str(idx),
                default=idx == self.weather_tracker.temperature_lvl + self.weather_tracker.get_temp_modifier()
            ) for idx, val in enumerate(temp_titles)
        ]
        wind_options = [
            SelectOption(
                label=val,
                value=str(idx),
                default=idx == self.weather_tracker.wind_lvl
            ) for idx, val in enumerate(wind_titles)
        ]
        rain_options = [
            SelectOption(
                label=val,
                value=str(idx),
                default=idx == self.weather_tracker.snow_rain_lvl
            ) for idx, val in enumerate(precip_titles)
        ]
        select_temp = Select(options=temp_options, custom_id="select_temp")
        select_wind = Select(options=wind_options, custom_id="select_wind")
        select_rain = Select(options=rain_options, custom_id="select_precipitation")

        async def update_view(interaction: Interaction):
            await edit_interaction_message(
                interaction,
                {
                    "embed": self.weather_tracker.get_weather_tracker_embed(),
                    "view": WeatherSelectView(self.weather_tracker)
                }
            )
            self.stop()

        async def set_temp(interaction: Interaction):
            self.update_weather_data(interaction)
            self.weather_tracker.temperature_lvl = int(select_temp.values[0])-self.weather_tracker.get_temp_modifier()
            await update_view(interaction)

        async def set_wind(interaction: Interaction):
            self.update_weather_data(interaction)
            self.weather_tracker.wind_lvl = int(select_wind.values[0])
            await update_view(interaction)

        async def set_rain(interaction: Interaction):
            self.update_weather_data(interaction)
            self.weather_tracker.snow_rain_lvl = int(select_rain.values[0])
            await update_view(interaction)

        select_temp.callback = set_temp
        select_wind.callback = set_wind
        select_rain.callback = set_rain

        self.add_item(select_temp)
        self.add_item(select_wind)
        self.add_item(select_rain)

    def update_weather_data(self, interaction: Interaction):
        self.weather_tracker = create_weather_tracker_from_fields(interaction.message.embeds[0])

    @button(label="roll", style=Bstyle.primary, row=0, emoji=PartialEmoji.from_str("☁"), custom_id="roll_weather")
    async def roll_weather(self, _: Button, interaction: Interaction):
        await roll_dc_logic(self, interaction)

    @button(label="stop edit", style=Bstyle.grey, row=0, emoji=PartialEmoji.from_str("✏"), custom_id="edit_weather")
    async def stop_edit_weather(self, _: Button, interaction: Interaction):
        self.update_weather_data(interaction)

        await edit_interaction_message(
            interaction,
            {
                "embed": self.weather_tracker.get_weather_tracker_embed(),
                "view": WeatherView(weather_tracker=self.weather_tracker)
            }
        )
        self.stop()

    @button(label="switch systems", style=Bstyle.gray, row=0, emoji=PartialEmoji.from_str("🗡"), custom_id="edit_system")
    async def switch_system_button(self, _: Button, interaction: Interaction):
        await switch_system(self, interaction)


async def roll_dc_logic(self, interaction):
    self.update_weather_data(interaction)
    text_delta = self.weather_tracker.roll()
    await edit_interaction_message(
        interaction,
        {
            "embed": self.weather_tracker.get_weather_tracker_embed(text_delta),
            "view": WeatherView(self.weather_tracker)
        }
    )
    self.stop()


async def switch_system(view, interaction: Interaction):
    view.update_weather_data(interaction)
    track = view.weather_tracker
    track.is_pathfinder = not track.is_pathfinder
    track.temperature_lvl = max(min(track.temperature_lvl, track.get_temp_modifier()), -track.get_temp_modifier())
    await edit_interaction_message(
        interaction,
        {
            "embed": view.weather_tracker.get_weather_tracker_embed(),
            "view": WeatherView(view.weather_tracker)
        }
    )
    view.stop()


def setup(bot: commands.Bot):
    init_data()
    # Every extension should have this function
    bot.add_cog(WeatherCog())
    bot.add_view(WeatherView(WeatherTracker()))
    bot.add_view(WeatherSelectView(WeatherTracker()))
    logger.info("weather extension loaded")
