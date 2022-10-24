from discord.ext.bridge import BridgeExtContext
import src.ext.Campaign.Undo as Undo
from .CampaignCog import CampaignCog
from .packg_variables import charDic
from .campaign_helper import get_char_name_if_none


async def test(ctx: BridgeExtContext, char_name=None):
    async def undo_redo(ctx):
        Undo.undo()
        Undo.redo()
        Undo.undo()

    def check(name, original_dict, actual_char_name):
        print(name)
        if not charDic.__contains__(actual_char_name):
            raise Exception("WE GOT PROBLEM")
        char_dict = charDic[actual_name].__dict__
        if any([origin != new for origin, new in zip(original_dict, char_dict)]):
            print("error")
            print("or", original_dict)
            print("char", char_dict)

    actual_name = get_char_name_if_none(char_name, ctx)
    original_dict = charDic[actual_name].__dict__
    testCog = CampaignCog()

    await testCog.crit(ctx, char_name)
    await undo_redo(ctx)
    check("crit", original_dict, actual_name)

    await testCog.dodged(ctx, char_name)
    await undo_redo(ctx)
    check("dodged", original_dict, actual_name)

    await testCog.cause(ctx, 15, char_name=char_name)
    await undo_redo(ctx)
    check("caused", original_dict, actual_name)

    await testCog.cause(ctx, 15, 2, char_name=char_name)
    await undo_redo(ctx)
    check("caused kills", original_dict, actual_name)

    await testCog.take(ctx, 2, char_name=char_name)
    await undo_redo(ctx)
    check("take", original_dict, actual_name)

    await testCog.take_reduced(ctx, 10, char_name=char_name)
    await undo_redo(ctx)
    check("take_r", original_dict, actual_name)

    await testCog.tank(ctx, 12, char_name=char_name)
    await undo_redo(ctx)
    check("tank", original_dict, actual_name)

    await testCog.set_max(ctx, 24, char_name=char_name)
    await undo_redo(ctx)
    check("set_max", original_dict, actual_name)

    await testCog.heal_single(ctx, 2, char_name=char_name)
    await undo_redo(ctx)
    check("heal", original_dict, actual_name)

    await testCog.heal_single(ctx, 2, char_name="all")
    await undo_redo(ctx)
    check("heal all", original_dict, actual_name)

    await testCog.full_h(ctx, char_name=char_name)
    await undo_redo(ctx)
    check("healm", original_dict, actual_name)

    await testCog.full_h(ctx, char_name="all")
    await undo_redo(ctx)
    check("healm all", original_dict, actual_name)

    await testCog.rename_player_character(ctx, actual_name, "testName")
    await undo_redo(ctx)
    check("rename", original_dict, actual_name)

    await testCog.file(ctx, "test2")
    await undo_redo(ctx)
    check("file", original_dict, actual_name)