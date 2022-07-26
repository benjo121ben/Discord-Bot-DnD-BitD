import os
from discord.ext import commands
from discord import File
import src.GlobalVariables as globalVars
from random import uniform

devils_bargain_images_path = "Assets/DB/"


@commands.command(name="db")
async def devils_bargain(ctx, *args):
    if not globalVars.devils_bargains_exist:
        await ctx.send("Devils Bargains are missing, therefore this command was automatically deactivated.")
        return

    if len(args) == 1 and args[0].isnumeric():
        amount = min(10, int(args[0]))
        file_list: list[File] = []
        for i in range(0, amount):
            file_list.append(get_devils_bargain())
        await ctx.send(files=file_list)
    else:
        await ctx.send(file=get_devils_bargain())


def get_devils_bargain():
    rand = int(uniform(1,50))
    if rand < 10:
        rand = "0" + str(rand)
    return File(devils_bargain_images_path + "DevilsBargain-" + str(rand) + ".png")


def check_devils_bargain():
    globalVars.devils_bargains_exist = True
    for i in range(1,50):
        nr = str(i)
        if i < 10:
            nr = "0" + str(i)
        if not os.path.exists(devils_bargain_images_path + "DevilsBargain-" + nr + ".png"):
            globalVars.devils_bargains_exist = False
            print("DevilsBargain-" + nr + ".png", "missing")
    if not globalVars.entanglements_exist:
        print("Devils Bargains disabled, due to missing Files")
    else:
        print("Devils Bargains present, feature enabled")


def setup(bot: commands.bot.Bot):
    # Every extension should have this function
    check_devils_bargain()
    bot.add_command(devils_bargain)
