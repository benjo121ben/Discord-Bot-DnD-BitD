from . import GlobalVariables
import logging

ext_base_path = "src.ext."
logger = logging.getLogger('bot')


def load_extensions(_bot, modules_list: list[bool] = None, reload=False):
    def load_ext(extension, ext_path=ext_base_path):
        if reload:
            _bot.reload_extension(ext_path + extension)
        else:
            _bot.load_extension(ext_path + extension)

    global logger
    logger.info("\n---------------------LOADING EXTENSIONS---------------------\n")
    if modules_list is not None:
        GlobalVariables.modules_list = modules_list
    if GlobalVariables.modules_list is None:
        load_ext("Campaign.CampaignCog")
        load_ext("BladesUtility.RollUtilityCog")
        load_ext("BladesUtility.BladesUtilityCog")
        load_ext("BladesUtility.ClockCog")
    else:
        if GlobalVariables.modules_list[0] or GlobalVariables.modules_list[1]:
            load_ext("BladesUtility.RollUtilityCog")

        if GlobalVariables.modules_list[0]:
            load_ext("Campaign.CampaignCog")
        if GlobalVariables.modules_list[1]:
            load_ext("BladesUtility.BladesUtilityCog")
            load_ext("BladesUtility.ClockCog")
        if GlobalVariables.modules_list[2]:
            load_ext("src.DebugCog", "")

    logger.info("---------------------EXTENSIONS LOADED---------------------\n")