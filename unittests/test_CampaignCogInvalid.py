import asyncio
from typing import Any, Coroutine

import pytest
from discord.ext.bridge import BridgeExtContext
from src.ext.Campaign.CampaignCog import CampaignCog
from src.ext.Campaign import Undo
from src.ext.Campaign import Character as char_file, packg_variables as packg_vars
from src.ext.Campaign.SaveDataManagement import \
    save_file_management as save_manager, \
    live_save_manager as live_manager, \
    char_data_access as char_access

from .test_const_vars import unit_test_save_file_name, test_user_id, test_char_tag, test_discord_username, \
    test_user_id_int, test_discord_username2
from .setup_mock_discord_objects import get_mocked_context, setup_bot_and_cog_campaign

from .unit_test_template_manager import cleanup_template


def delete_present_save_file():
    if save_manager.check_savefile_existence(unit_test_save_file_name):
        save_manager.remove_save_file(unit_test_save_file_name)
        cleanup_template()
        print("deleted existing unit test savefile")


def setup() -> tuple[CampaignCog, BridgeExtContext]:
    delete_present_save_file()
    cog = setup_bot_and_cog_campaign()
    ctx = get_mocked_context(test_user_id_int)
    return cog, ctx


def assert_char_value_base_save(char_tag: str, attribute_name: str, value: Any):
    assert char_access.get_char(test_user_id, char_tag).__dict__[attribute_name] == value
    assert save_manager.character_from_save_file(unit_test_save_file_name, char_tag).__dict__[attribute_name] == value


def assert_save_value_base_save(attribute_name: str, value: Any):
    assert live_manager.get_loaded_dict(test_user_id)[attribute_name] == value
    assert save_manager.save_file_to_parsed_dictionary(unit_test_save_file_name)[attribute_name] == value


def assert_ctx_any_respond(ctx, *args, **kwargs):
    ctx.respond.assert_any_call(*args, **kwargs)


async def assert_command(value: Coroutine):
    assert await value


async def assert_failed_command(value: Coroutine, undo_len: int):
    assert not await value
    assert len(Undo.get_action_queue(test_user_id)) == undo_len


class TestCampaignCogInvalid:
    @pytest.fixture
    def create_cog_and_load(self):
        cog, ctx = setup()
        asyncio.run(cog.load_command(ctx, unit_test_save_file_name))
        print("setup done")
        yield cog, ctx
        cleanup_template()
        print("teardown done")

    @pytest.fixture
    def create_char(self, create_cog_and_load: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_cog_and_load
        asyncio.run(cog.add_c(ctx, test_char_tag, "test"))
        yield cog, ctx

    @pytest.fixture
    def create_own_char(self, create_cog_and_load: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_cog_and_load
        asyncio.run(cog.add_c(ctx, test_char_tag, "test", test_user_id))
        yield cog, ctx

    @pytest.mark.asyncio
    async def test_invalid_creation(self, create_cog_and_load: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_cog_and_load
        assert str(ctx.author.id) == test_user_id
        await assert_command(cog.add_c(ctx, test_char_tag, "test"))
        assert len(Undo.get_action_queue(test_user_id)) == 2

        #repeated add
        await assert_failed_command(cog.add_c(ctx, test_char_tag, "test"), 2)

        #invalid add
        await assert_failed_command(cog.add_c(ctx, "all", "test"), 2)

        # add enough characters to fill up
        for i in range(9):
            await assert_command(cog.add_c(ctx, str(i), "test"))

        #failed cause too many characters
        await assert_failed_command(cog.add_c(ctx, "ttt", "test"), 10)

