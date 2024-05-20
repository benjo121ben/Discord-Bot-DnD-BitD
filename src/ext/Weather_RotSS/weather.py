import logging
from os.path import exists
import os
import json
import pathlib
import random

from discord import Embed

relative_asset_folder_path = os.sep.join(['Assets', ''])

logger = logging.getLogger('bot')

# This base functionality is from Raiders of the Serpent Sea

weather_tracker_text_data = {}


def get_text_data_path():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, relative_asset_folder_path, 'text_data.json')


def find_weather_data_values_from_fields(embed: Embed):
    def search_list(l, value):
        for idx, obj in enumerate(l):
            if obj["title"] == value:
                return idx
        return -99
    global weather_tracker_text_data
    temp: int = search_list(weather_tracker_text_data["temp"], embed.fields[0].name.replace("*", "")) - 5
    wind: int = search_list(weather_tracker_text_data["wind"], embed.fields[1].name.replace("*", ""))
    weather = -99
    if temp <= -2:
        weather = search_list(weather_tracker_text_data["snow"], embed.fields[2].name.replace("*", ""))
    else:
        weather = search_list(weather_tracker_text_data["rain"], embed.fields[2].name.replace("*", ""))
    return [temp, wind, weather]


def init_data():
    global weather_tracker_text_data
    if not exists(get_text_data_path()):
        raise Exception("Weather text data does not exist.")
    else:
        with open(get_text_data_path()) as data:
            weather_tracker_text_data = json.load(data)


def get_titles():
    global weather_tracker_text_data
    temp = [val["title"] for val in weather_tracker_text_data["temp"]]
    wind = [val["title"] for val in weather_tracker_text_data["wind"]]
    precip = [
        "Clear",
        "Cloudy",
        "Light Snow/Rain",
        "Heavy Snow/Rain"
    ]
    return temp, wind, precip


class WeatherTracker:
    temperature_lvl: int = 0
    wind_lvl: int = 0
    snow_rain_lvl: int = 0

    def __init__(self, temp: int = 0, wind: int = 0, snow: int = 0):
        self.temperature_lvl = temp
        self.wind_lvl = wind
        self.snow_rain_lvl = snow

    def get_weather_tracker_embed(self, delta=None):
        embed = Embed()
        if delta:
            embed.description = (
                f'**Temperature**:   {delta[0]}\n'
                f'**Wind**:          {delta[1]}\n'
                f'**Precipitation**: {delta[2]}\n'
                f'---'
            )
        else:
            embed.description = ""

        columns = [
            weather_tracker_text_data['temp'][self.temperature_lvl+5],
            weather_tracker_text_data['wind'][self.wind_lvl],
            weather_tracker_text_data['snow'][self.snow_rain_lvl] if self.temperature_lvl <= -2 else weather_tracker_text_data['rain'][self.snow_rain_lvl]
        ]

        for entry in columns:
            embed.add_field(name=f"*{entry['title']}*", value=entry["description"])

        return embed

    def __str__(self):
        return f"{self.temperature_lvl}, {self.wind_lvl}, {self.snow_rain_lvl}"

    def roll(self) -> [int, int, int]:

        def roll_temp():
            d20 = random.randint(1, 20)
            if d20 <= 2:
                return 2
            elif d20 <= 6:
                return 1
            elif d20 <= 16:
                return 0
            elif d20 <= 19:
                return -1
            elif d20 <= 20:
                return -2

        def roll_wind():
            d12 = random.randint(1, 12)
            if d12 <= 1:
                return -2
            elif d12 <= 3:
                return -1
            elif d12 <= 7:
                return 0
            elif d12 <= 10:
                return 1
            elif d12 <= 12:
                return 2

        def roll_snow():
            d10 = random.randint(1, 10)
            if d10 <= 1:
                return -2
            elif d10 <= 3:
                return -1
            elif d10 <= 5:
                return 0
            elif d10 <= 8:
                return 1
            elif d10 <= 10:
                return 2

        delta = [roll_temp(), roll_wind(), roll_snow()]
        text_delta = [
            weather_tracker_text_data['inc_temp'][delta[0]+2],
            weather_tracker_text_data['inc_wind'][delta[1]+2],
            weather_tracker_text_data['inc_snow'][delta[2]+2]
        ]

        self.temperature_lvl = max(min(self.temperature_lvl + delta[0], 5), -5)
        self.wind_lvl = max(min(self.wind_lvl + delta[1], 3), 0)
        self.snow_rain_lvl = max(min(self.snow_rain_lvl + delta[2], 3), 0)

        return text_delta
