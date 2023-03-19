from typing import Callable
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import discord
from discord.ext.bridge import BridgeExtContext, Bot

from src.ext.Campaign import CampaignCog as camp_cog, packg_variables as p_vars

from .test_const_vars import test_discord_username, test_discord_username2, test_user_id


def get_mocked_context(author_id: int) -> BridgeExtContext:
    class MockedAuthor:
        def __init__(self, user_id: int):
            self.id = user_id

    ctx = mock.MagicMock(BridgeExtContext)
    ctx.author = MockedAuthor(author_id)
    ctx.respond = AsyncMock(discord.ext.bridge.BridgeExtContext.respond, side_effect=lambda *args, **kwargs: print(f"mock_respond:{{\n{args[0]}\n}}"))
    ctx.send = AsyncMock(side_effect=lambda message: print(f"mock_send:{{\n{message}\n}}"))
    return ctx


def get_mocked_bot(cog_func) -> Bot:
    class MockChannel:
        def history(self, limit):
            return self

        def next(self):
            return self

        async def send(self, *args, **kwargs):
            return "sent"

    bot = mock.MagicMock(Bot)
    user = mock.MagicMock(discord.User)
    user.name = test_discord_username
    user2 = mock.MagicMock(discord.User)
    user2.name = test_discord_username2
    bot.add_cog = MagicMock(return_value=None, side_effect=lambda c: cog_func(c))
    bot.fetch_user = AsyncMock(bot.fetch_user, side_effect=lambda user_id: user if str(user_id) == test_user_id else user2)

    bot.get_channel = MagicMock(discord.Bot.get_channel, return_value=MockChannel())
    return bot


def setup_bot_and_cog(setup_func: Callable[[Bot], None]) -> discord.ext.commands.Cog:
    cog: discord.ext.commands.Cog = None

    def set_cog(c):
        nonlocal cog
        cog = c
    p_vars.bot = get_mocked_bot(set_cog)
    setup_func(p_vars.bot)

    return cog


def setup_bot_and_cog_campaign() -> camp_cog.CampaignCog:
    return setup_bot_and_cog(camp_cog.setup)
