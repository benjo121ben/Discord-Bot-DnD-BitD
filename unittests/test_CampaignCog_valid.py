import asyncio
from typing import Any

import pytest
from discord.ext.bridge import BridgeExtContext

from src.ext.Campaign.CampaignCog import CampaignCog
from src.ext.Campaign import Character as char_file
from src.ext.Campaign.SaveDataManagement import \
    save_file_management as save_manager, \
    live_save_manager as live_manager, \
    char_data_access as char_access

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


def assert_char_value_base_save(char_tag: str, attribute_name: str, value: Any):
    assert char_access.get_char(test_user_id, char_tag).__dict__[attribute_name] == value
    assert save_manager.character_from_save_file(unit_test_save_file_name, char_tag).__dict__[attribute_name] == value


class TestCampaignCog_valid:
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
    async def test_creation(self, create_cog_and_load: tuple[CampaignCog, BridgeExtContext]):
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
    async def test_creation_with_user(self, create_cog_and_load: tuple[CampaignCog, BridgeExtContext]):
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
    async def test_crit(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 0)
        await cog.crit(ctx, 1, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 1)
        await cog.crit(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 3)
        await cog.crit(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 4)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 3)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 1)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CRITS, 4)

    @pytest.mark.asyncio
    async def test_faint(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 0)
        await cog.faint(ctx, 1, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 1)
        await cog.faint(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 3)
        await cog.faint(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 4)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 3)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 1)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_FAINTS, 4)

    @pytest.mark.asyncio
    async def test_dodged(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 0)
        await cog.dodged(ctx, 1, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 1)
        await cog.dodged(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 3)
        await cog.dodged(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 4)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 3)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 1)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_DODGE, 4)

    @pytest.mark.asyncio
    async def test_cause(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 0)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 0)
        await cog.cause(ctx, 30)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 30)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 0)
        await cog.cause(ctx, 20, 1)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 50)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 1)
        await cog.cause(ctx, 20, 3, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 70)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 4)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 50)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 1)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 0)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 30)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 0)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_CAUSED, 70)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_KILLS, 4)

    @pytest.mark.asyncio
    async def test_take(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 0)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.take(ctx, 30, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 30)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.take(ctx, 20)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 50)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.take(ctx, 20)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 70)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 50)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 0)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 30)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 70)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)

    @pytest.mark.asyncio
    async def test_take_resisted(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 0)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.take_reduced(ctx, 30, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 15)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 15)
        await cog.take_reduced(ctx, 9)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 19)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 20)
        await cog.take_reduced(ctx, 20)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 29)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 30)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 19)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 20)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 0)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 15)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 15)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAKEN, 29)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_RESISTED, 30)

    @pytest.mark.asyncio
    async def test_heal(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 0)
        await cog.heal(ctx, 10, test_char_tag)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 10)
        await cog.heal(ctx, 10)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 20)
        await cog.heal(ctx, 5)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 25)
        await cog.undo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 10)
        await cog.undo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 0)
        await cog.redo(ctx)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 10)
        await cog.redo(ctx, 2)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_HEALED, 25)

    @pytest.mark.asyncio
    async def test_retag(self, create_own_char: tuple[CampaignCog, BridgeExtContext]):
        cog, ctx = create_own_char
        NEW_TAG = "new_tag"
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAG, test_char_tag)
        await cog.retag_pc(ctx, test_char_tag, NEW_TAG)
        with pytest.raises(Exception):
            save_manager.character_from_save_file(unit_test_save_file_name, test_char_tag)
        assert_char_value_base_save(NEW_TAG, char_file.LABEL_TAG, NEW_TAG)
        await cog.undo(ctx)
        with pytest.raises(Exception):
            save_manager.character_from_save_file(unit_test_save_file_name, NEW_TAG)
        assert_char_value_base_save(test_char_tag, char_file.LABEL_TAG, test_char_tag)
        await cog.redo(ctx)
        assert_char_value_base_save(NEW_TAG, char_file.LABEL_TAG, NEW_TAG)

