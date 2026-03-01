import os
import logging
import pathlib
from os.path import exists
from discord import File
from datetime import datetime
from random import uniform, seed


seed(datetime.now().timestamp())
devils_bargains_enabled = False
logger = logging.getLogger('bot')
db_asset_folder_rel_path = os.sep.join(["Assets", "DB", ""])


def get_db_asset_folder_filepath():
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, db_asset_folder_rel_path)


def check_devils_bargain_assets():
    global devils_bargains_enabled
    if not exists(get_db_asset_folder_filepath()):
        logger.error(f"Cannot find devils bargain asset folder:\n"
                     f"{get_db_asset_folder_filepath()}"
                     f"Devils Bargain Feature disabled")
        return
    devils_bargains_enabled = True
    for i in range(1, 50):
        nr = str(i)
        if i < 10:
            nr = "0" + str(i)
        if not os.path.exists(get_db_asset_folder_filepath() + "DevilsBargain-" + nr + ".png"):
            devils_bargains_enabled = False
            logger.warning("DevilsBargain-" + nr + ".png", "missing")
    if not devils_bargains_enabled:
        logger.warning("Devils Bargains disabled, due to missing Files")
    else:
        logger.info("Devils Bargains present, feature enabled")


def get_devils_bargain():
    rand = int(uniform(1, 50))
    if rand < 10:
        rand = "0" + str(rand)
    return File(f"{get_db_asset_folder_filepath()}DevilsBargain-{rand}.png")


async def db_functionality(ctx, amount: int = 1):
    if not devils_bargains_enabled:
        await ctx.respond("Devils Bargains are missing, therefore this command was automatically deactivated.")
        return

    if amount > 1:
        amount = min(10, amount)
        file_list: list[File] = []
        for i in range(0, amount):
            file_list.append(get_devils_bargain())
        await ctx.respond(files=file_list)
    else:
        await ctx.respond(file=get_devils_bargain())


async def db_single_functionality(ctx, nr: int):
    if not devils_bargains_enabled:
        await ctx.respond("Devils Bargains are missing, therefore this command was automatically deactivated.")
        return

    if not 0 < nr < 51:
        ctx.respond("A card with this number does not exist.")
        return

    if nr < 10:
        nr = "0" + str(nr)
    await ctx.respond(file=File(get_db_asset_folder_filepath() + "DevilsBargain-" + str(nr) + ".png"))
