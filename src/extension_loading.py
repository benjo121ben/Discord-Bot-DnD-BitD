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
    logger.info("---------------------LOADING EXTENSIONS---------------------")
    if modules_list is not None:
        GlobalVariables.modules_list = modules_list
    if GlobalVariables.modules_list is None:
        load_ext("Campaign.CampaignCog")
        load_ext("BladesUtility.RollUtilityCog")
        load_ext("BladesUtility.BladesUtilityCog")
        load_ext("BladesUtility.ClockCog")
        load_ext("Weather_RotSS.WeatherCog")
        load_ext("DebugCog", "src.")
    else:
        load_ext("DebugCog", "src.")
        if GlobalVariables.modules_list[0] or GlobalVariables.modules_list[1]:
            load_ext("BladesUtility.RollUtilityCog")

        if GlobalVariables.modules_list[0]:
            load_ext("Campaign.CampaignCog")
        if GlobalVariables.modules_list[1]:
            load_ext("BladesUtility.ResourcesCog")
            load_ext("BladesUtility.BladesUtilityCog")
            load_ext("Clocks.ClockCog")
        if GlobalVariables.modules_list[2]:
            load_ext("Kanka.KankaCog")
        if GlobalVariables.modules_list[3]:
            load_ext("Weather_RotSS.WeatherCog")

    logger.info("---------------------EXTENSIONS LOADED---------------------")
