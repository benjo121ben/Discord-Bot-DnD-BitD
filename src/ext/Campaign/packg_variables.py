from .Character import Character
import os

campaign_env_file_rel_path = os.sep.join(['..', '..', '..', '.env'])
saves_location_relative_to_module = os.sep.join(['..', '..', '..', 'saves'])
cache_location_relative_to_module = os.sep.join(['..', '..', '..', 'saves', 'cache'])

cache_folder: int = None
bot_admin_id: int = None

charDic: dict[str, Character] = {}
localCommDic = {}
imported_dic = {}

