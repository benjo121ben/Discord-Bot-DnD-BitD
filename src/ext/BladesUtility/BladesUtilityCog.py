import os
import random
from PIL import Image
from discord import slash_command, File
from discord.ext import commands
from discord.ext import bridge
from . import functions as bitd_func


class BladesUtilityCog(commands.Cog):

    @slash_command(name="devils_bargain", description="Returns one or more random devils bargain cards. Default: 1 card")
    async def devils_bargain(self, ctx, nr: int = 1):
        await bitd_func.db_functionality(ctx, nr)

    @slash_command(name="db_by_nr", description="Returns the Devils Bargain Card with with this number")
    async def devils_bargain_by_nr(self, ctx, nr: int):
        await bitd_func.db_single_functionality(ctx, nr)

    @slash_command(name="entanglement", description="Prints out the entanglement choices for the given rolled value and heat")
    async def entanglements(self, ctx, rolled: int, heat: int):
        await bitd_func.entanglement_functionality(ctx, rolled, heat)

    @slash_command(name="b_roll", description="tests the blades roll")
    async def blades_roll(self, ctx, dice_amount: int):
        try:
            erg, rolled_array = bitd_func.get_blades_roll(dice_amount)
            spritesheet = Image.open(bitd_func.get_spritesheet_filepath()).convert('RGBA')
            sheet_size = spritesheet.size
            dice_sprite_size = bitd_func.get_sprite_size()
            end_image_length = dice_sprite_size * dice_amount if dice_amount > 0 else 2 * dice_sprite_size
            end_image_height = dice_sprite_size
            new_image = Image.new('RGBA', (end_image_length, end_image_height), (250, 250, 250))
            # Read the two images
            all_rolls_index = 0
            for array_index, amount_rolled in enumerate(rolled_array):
                nr_rolled = 6 - array_index
                if nr_rolled == 6 and erg == 2:
                    nr_rolled = 7
                nr_image = bitd_func.get_sprite_from_uniform_spritesheet(spritesheet, dice_sprite_size, nr_rolled-1)
                for _ in range(amount_rolled):
                    new_image.paste(nr_image, (dice_sprite_size * all_rolls_index, 0), nr_image)
                    all_rolls_index += 1
            success_file_path = bitd_func.get_asset_folder_filepath() + "success.png"
            merged_file_path = bitd_func.get_asset_folder_filepath() + "merged.png"

            bitd_func.get_success_tag_sprite(erg).save(success_file_path, "PNG")
            new_image.resize((end_image_length * 2, end_image_height * 2), resample=0).save(merged_file_path, "PNG")

            await ctx.respond(files=[File(success_file_path), File(merged_file_path)])
            os.remove(success_file_path)
            os.remove(merged_file_path)
        except bitd_func.BladesCommandException as e:
            await ctx.respond(str(e))

    @slash_command(name="roll", description="tests the all roll")
    async def types_roll(self, ctx, dice_amount: int, dice_type: int):
        rolled_array = bitd_func.get_roll(dice_amount, dice_type)
        base_image = Image.open(bitd_func.get_die_base_image_filepath(dice_type)).convert('RGBA')
        new_dice_size = base_image.size
        new_image = Image.new('RGBA', (new_dice_size[0] * dice_amount, new_dice_size[1]), (250, 250, 250))
        # Read the two images
        index = 0
        for nr_rolled, amount_rolled in enumerate(rolled_array):
            for _ in range(amount_rolled):
                nr_image = Image.open(bitd_func.get_die_nr_image_filepath(nr_rolled + 1)).convert('RGBA')
                new_image.paste(base_image, (0 + 150 * index, 0))
                new_image.paste(nr_image, (50 + 150 * index, 50), nr_image)
                index += 1
        merged_file_path = bitd_func.get_asset_folder_filepath() + "merged.png"
        new_image.save(merged_file_path, "PNG")
        await ctx.respond(file=File(merged_file_path))
        os.remove(merged_file_path)


def setup(bot: bridge.Bot):
    # Every extension should have this function
    print("loading Entanglements")
    bitd_func.check_entanglements()
    bitd_func.check_devils_bargain()
    bot.add_cog(BladesUtilityCog())


