import asyncio

import pytest
from src.ext.Campaign import CommandFunctions as commands
from src.ext.Campaign import CampaignCog as camp_cog
from src.ext.Campaign import packg_variables as p_vars
from src.ext.Campaign.SaveDataManagement import save_file_management as save_manager, live_save_manager as live_manager, char_data_access as char_access

from .test_const_vars import unit_test_save_file_name, test_user_id, test_char_tag, test_discord_username, \
    get_mocked_bot, get_mocked_context

from .unit_test_template_manager import move_template_save_to_save_folder, cleanup_template


class TestCampaignCog:
    @pytest.fixture
    def create_cog_and_load(self):
        cog: camp_cog.CampaignCog = None

        def set_cog(c):
            nonlocal cog
            cog = c

        if save_manager.check_savefile_existence(unit_test_save_file_name):
            save_manager.remove_file(unit_test_save_file_name)
            cleanup_template()
            print("deleted existing unit test savefile")
        p_vars.bot = get_mocked_bot(set_cog)
        camp_cog.setup(p_vars.bot)
        ctx = get_mocked_context()
        asyncio.run(cog.load_command(ctx, unit_test_save_file_name))
        print("setup done")
        yield cog, ctx
        cleanup_template()
        print("teardown done")

    def test_test(self, create_cog_and_load):
        cog, ctx = create_cog_and_load
        print(ctx.author.id)
        assert ctx.author.id == test_user_id
        asyncio.run(cog.add_c(ctx, test_char_tag, "test"))
        print(commands.add_char(test_user_id, test_char_tag, "test"))
        print(commands.log(test_user_id))
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