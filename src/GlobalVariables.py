import os
from discord.ext.commands import Bot
admin_id: str = None
modules_list: list[bool] = None
bot: Bot = None
env_file_rel_path = f'.{os.sep}.env'
bot_host_email: str = ""
logger = None

