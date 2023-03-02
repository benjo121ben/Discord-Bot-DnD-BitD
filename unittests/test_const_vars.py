import logging
import os
from unittest import mock
from unittest.mock import MagicMock, AsyncMock, Mock

import discord
from discord.ext.bridge import BridgeExtContext
from src.ext.Campaign.campaign_helper import get_bot

unit_test_save_file_name = "unit_test"
test_user_id: str = "0"
test_char_tag: str = "test"
test_discord_username: str = "TEST_DISCORD_USERNAME"
template_save_folder_relative_path: str = os.sep.join(["test_saves"])

logger = logging.getLogger('testContext')


def get_mocked_context() -> BridgeExtContext:
    class MockedAuthor:
        def __init__(self, user_id: str):
            self.id = user_id

    ctx = BridgeExtContext(bot=get_bot(), message=mock.MagicMock(discord.Message), view=None)
    ctx.author = MockedAuthor(test_user_id)
    ctx.respond = AsyncMock(side_effect=lambda message: logger.info(f"mock_respond:{message}"))
    ctx.send = AsyncMock(side_effect=lambda message: logger.info(f"mock_send:{message}"))
    return ctx


def get_mocked_bot(cog_func) -> discord.ext.bridge.Bot:
    class MockChannel:
        def history(self, limit):
            return self

        def next(self):
            return self

        async def send(self, *args, **kwargs):
            return "sent"

    bot = discord.ext.bridge.Bot()
    bot.add_cog = MagicMock(return_value=None, side_effect=lambda c: cog_func(c))
    bot.fetch_user = MagicMock(return_value=test_discord_username)

    bot.get_channel = MagicMock(return_value=MockChannel())
    return bot


