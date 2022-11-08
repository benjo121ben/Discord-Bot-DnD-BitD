from .Character import Character

campaign_env_file_rel_path = '..\\..\\..\\.env'
saves_location_relative_to_module = '..\\..\\..\\saves'
cache_location_relative_to_module = '..\\..\\..\\saves\\cache'

cache_folder: int = None
bot_admin_id: int = None

charDic: dict[str, Character] = {}
localCommDic = {}
imported_dic = {}

