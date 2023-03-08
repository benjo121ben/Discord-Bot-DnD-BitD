import asyncio

import pytest
from discord.ext.bridge import BridgeExtContext

from src.ext.Campaign.CampaignCog import CampaignCog
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager, live_save_manager as live_manager, char_data_access as char_access

from .test_const_vars import unit_test_save_file_name, test_user_id, test_char_tag, test_discord_username, \
    test_user_id_int
from .setup_mock_discord_objects import get_mocked_context, get_mocked_bot, setup_bot_and_cog_campaign

from .unit_test_template_manager import move_template_save_to_save_folder, cleanup_template


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


class TestCampaignCog:
    @pytest.fixture
    def create_cog_and_load(self):
        cog, ctx = setup()
        asyncio.run(cog.load_command(ctx, unit_test_save_file_name))
        print("setup done")
        yield cog, ctx
        cleanup_template()
        print("teardown done")

    @pytest.fixture
    def create_char(self, create_cog_and_load):
        cog, ctx = create_cog_and_load
        asyncio.run(cog.add_c(ctx, test_char_tag, "test"))
        yield cog, ctx

    @pytest.fixture
    def create_own_char(self, create_cog_and_load):
        cog, ctx = create_cog_and_load
        asyncio.run(cog.add_c(ctx, test_char_tag, "test", test_user_id))
        yield cog, ctx

    @pytest.mark.asyncio
    async def test_creation(self, create_cog_and_load):
        cog, ctx = create_cog_and_load
        assert str(ctx.author.id) == test_user_id
        await cog.add_c(ctx, test_char_tag, "test")
        assert save_manager.check_savefile_existence(unit_test_save_file_name)
        _char = char_access.get_char(test_user_id, test_char_tag)
        assert _char.name == "test"
        assert _char.tag == test_char_tag
        assert _char.player == ""
        assert _char.damage_caused == 0
        assert _char.damage_healed == 0
        assert _char.damage_resisted == 0
        assert _char.damage_taken == 0
        assert _char.max_damage == 0
        assert _char.faints == 0
        assert _char.kills == 0
        assert _char.crits == 0
        assert _char.dodged == 0

    @pytest.mark.asyncio
    async def test_creation_with_user(self, create_cog_and_load):
        cog, ctx = create_cog_and_load
        assert str(ctx.author.id) == test_user_id
        await cog.add_c(ctx, test_char_tag, "test", test_user_id)
        assert save_manager.check_savefile_existence(unit_test_save_file_name)
        _char = char_access.get_char(test_user_id, test_char_tag)
        assert _char.name == "test"
        assert _char.tag == test_char_tag
        assert _char.player == test_user_id
        assert _char.damage_caused == 0
        assert _char.damage_healed == 0
        assert _char.damage_resisted == 0
        assert _char.damage_taken == 0
        assert _char.max_damage == 0
        assert _char.faints == 0
        assert _char.kills == 0
        assert _char.crits == 0
        assert _char.dodged == 0

    @pytest.mark.asyncio
    async def test_crit(self, create_own_char):
        cog, ctx = create_own_char
        assert str(ctx.author.id) == test_user_id
        assert char_access.get_char(test_user_id, test_char_tag).crits == 0
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).crits == 0
        await cog.crit(ctx, test_char_tag)
        assert char_access.get_char(test_user_id, test_char_tag).crits == 1
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).crits == 1
        await cog.crit(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).crits == 2
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).crits == 2
        await cog.undo(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).crits == 1
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).crits == 1
        await cog.undo(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).crits == 0
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).crits == 0

    @pytest.mark.asyncio
    async def test_faint(self, create_own_char):
        cog, ctx = create_own_char
        assert str(ctx.author.id) == test_user_id
        assert char_access.get_char(test_user_id, test_char_tag).faints == 0
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).faints == 0
        await cog.faint(ctx, test_char_tag)
        assert char_access.get_char(test_user_id, test_char_tag).faints == 1
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).faints == 1
        await cog.faint(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).faints == 2
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).faints == 2
        await cog.undo(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).faints == 1
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).faints == 1
        await cog.undo(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).faints == 0
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).faints == 0

    @pytest.mark.asyncio
    async def test_dodged(self, create_own_char):
        cog, ctx = create_own_char
        assert str(ctx.author.id) == test_user_id
        assert char_access.get_char(test_user_id, test_char_tag).dodged == 0
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).dodged == 0
        await cog.dodged(ctx, test_char_tag)
        assert char_access.get_char(test_user_id, test_char_tag).dodged == 1
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).dodged == 1
        await cog.dodged(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).dodged == 2
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).dodged == 2
        await cog.undo(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).dodged == 1
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).dodged == 1
        await cog.undo(ctx)
        assert char_access.get_char(test_user_id, test_char_tag).dodged == 0
        assert save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag).dodged == 0




