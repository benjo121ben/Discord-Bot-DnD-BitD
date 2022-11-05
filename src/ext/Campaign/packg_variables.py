from .Character import Character

campaign_dotenv_filepath = './.env'

cache_folder: int = None
bot_admin_id: int = None

charDic: dict[str, Character] = {}
localCommDic = {}
imported_dic = {}

