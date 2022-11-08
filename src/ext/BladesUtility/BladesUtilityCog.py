import os
import random
from PIL import Image
from discord import slash_command, File
from discord.ext import commands
from discord.ext import bridge
from .functions import db_functionality, db_single_functionality, check_devils_bargain, \
    entanglement_functionality, check_entanglements, get_blades_roll, get_db_asset_folder_filepath, \
    get_die_nr_image_filepath, get_die_base_image_filepath


class BladesUtilityCog(commands.Cog):

    @slash_command(name="devils_bargain", description="Returns one or more random devils bargain cards. Default: 1 card")
    async def devils_bargain(self, ctx, nr: int = 1):
        await db_functionality(ctx, nr)

    @slash_command(name="db_by_nr", description="Returns the Devils Bargain Card with with this number")
    async def devils_bargain_by_nr(self, ctx, nr: int):
        await db_single_functionality(ctx, nr)

    @slash_command(name="entanglement", description="Prints out the entanglement choices for the given rolled value and heat")
    async def entanglements(self, ctx, rolled: int, heat: int):
        await entanglement_functionality(ctx, rolled, heat)

    @slash_command(name="roll", description="tests the blades roll")
    async def blades_roll(self, ctx, dice: int, type: int):
        erg, rolled_array = get_blades_roll(dice)
        base_image = Image.open(get_die_base_image_filepath(type))
        new_dice_size = base_image.size
        new_image = Image.new('RGBA', (new_dice_size[0]*dice, new_dice_size[1]), (250, 250, 250))
        # Read the two images
        index = 0
        for nr_rolled, amount_rolled in enumerate(rolled_array):
            for _ in range(amount_rolled):
                nr_image = Image.open(get_die_nr_image_filepath(nr_rolled+1)).convert('RGBA')
                new_image.paste(base_image, (0 + 150 * index, 0))
                new_image.paste(nr_image, (50 + 150 * index, 50), nr_image)
                index += 1
        merged_file_path = get_db_asset_folder_filepath() + "merged.png"
        new_image.save(merged_file_path, "PNG")
        await ctx.respond(file=File(merged_file_path))
        # os.remove(merged_file_path)


def setup(bot: bridge.Bot):
    # Every extension should have this function
    print("loading Entanglements")
    check_entanglements()
    check_devils_bargain()
    bot.add_cog(BladesUtilityCog())


