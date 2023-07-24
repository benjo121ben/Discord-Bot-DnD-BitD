import json
import os
import pathlib
import logging
from os.path import exists

from discord import Embed
from discord.ext.bridge import BridgeExtContext

from .Dice import get_blades_roll_sorted
from .Entanglement_table import entanglement_sorting_table

logger = logging.getLogger('bot')
imported_expanded_entanglements = {}
asset_folder_rel_path = os.sep.join(["Assets", ""])
entanglements_enabled = False


def get_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, asset_folder_rel_path)


async def entanglement_wanted_functionality(ctx: BridgeExtContext, wanted: int, heat:int):
    erg, dice_array = get_blades_roll_sorted(wanted)
    for i in range(0, 6):
        if wanted > 0 and dice_array[i] > 0:  # search biggest number
            await entanglement_functionality(ctx, 6 - i, heat)
            return
        elif wanted == 0 and dice_array[5-i] > 0:  # search smallest number
            await entanglement_functionality(ctx, 1 + i, heat)
            return


async def entanglement_functionality(ctx: BridgeExtContext, rolled: int, heat: int):
    if not entanglements_enabled:
        await ctx.respond("Entanglements are missing, therefore this command was automatically deactivated.")
        return

    column = -1
    if heat <= 3:
        column = 0
    elif heat <= 5:
        column = 1
    else:
        column = 2

    if rolled < 1 or rolled > 6:
        await ctx.respond("The number rolled has to be between 1 and 6")
        return
    rolled -= 1
    ent_list = entanglement_sorting_table[column][rolled]
    embed = Embed(title="Entanglements", description="choose one!")
    for entanglement in ent_list:
        embed.add_field(name=entanglement, value=imported_expanded_entanglements[entanglement], inline=True)
    await ctx.respond(embed=embed)


def check_entanglement_assets():
    global imported_expanded_entanglements, entanglements_enabled
    expanded_entanglement_path = os.sep.join([f'{get_asset_folder_filepath()}', 'Expanded_Entanglements.json'])
    if not exists(expanded_entanglement_path):
        logger.error(f"Expanded_Entanglements.json cannot be found at location:\n"
                     f"{get_asset_folder_filepath()}\n"
                     f"entanglements disabled")
        return

    entanglements_enabled = True
    with open(expanded_entanglement_path)as file:
        imported_expanded_entanglements = json.load(file)
    logger.debug("looking for entanglements")
    for column in entanglement_sorting_table:
        for roll in column:
            for entanglement in roll:
                if entanglement not in imported_expanded_entanglements:
                    entanglements_enabled = False
                    logger.debug("missing", entanglement)

    if not entanglements_enabled:
        logger.warning("Entanglements disabled, due to entanglements missing in json file\n")
    else:
        logger.info("All Entanglement info present, feature enabled\n")
